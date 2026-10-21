"""The series explorer (docs/REQUISITOS.md §7.2): one or more parameters, each at its own points and
sources, between two dates, with descriptive statistics per series. Parameters with the same unit
share a chart.

The statistics always use the measurements themselves; the daily, weekly or monthly aggregation
only changes what the chart draws, so long series stay readable.
"""

import datetime
import json
import re
from dataclasses import dataclass

from django import forms
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone

from apps.catalog.models import Limit, Parameter, SamplingPoint, Source, Variable

from .charts import chart_data, point_color, source_shapes
from .models import MAX_POINTS
from .stats import Description, Exceedance, LimitBook, Period, count_suspect, describe, load_samples

DEFAULT_DAYS = 90
AUTO = "auto"
RAW = "none"
AGGREGATIONS = [
    (AUTO, "Automática"),
    (RAW, "Sin agregar"),
    (Period.DAY, "Promedio diario"),
    (Period.WEEK, "Promedio semanal"),
    (Period.MONTH, "Promedio mensual"),
]
PERIOD_NAMES = {Period.DAY: "promedios diarios", Period.WEEK: "promedios semanales", Period.MONTH: "promedios mensuales"}


def automatic_period(first_day, last_day):
    """Raw values up to three months, daily means up to three years, weekly means beyond."""
    days = (last_day - first_day).days + 1
    if days <= 92:
        return None
    if days <= 1100:
        return Period.DAY
    return Period.WEEK


def point_choices(parameter):
    return SamplingPoint.objects.filter(pk__in=Variable.objects.filter(parameter=parameter).values("point")).select_related("area")


def source_choices(parameter):
    return Source.objects.filter(pk__in=Variable.objects.filter(parameter=parameter).values("source"))


BLOCK_PREFIX = re.compile(r"^p(\d+)-parameter$")


def block_numbers(data):
    """The numbers of the parameter blocks in a request (p1-parameter, p3-parameter…), in order."""
    return sorted(int(match[1]) for key in data for match in [BLOCK_PREFIX.match(key)] if match)


class ParameterBlockForm(forms.Form):
    """A parameter with its own points and sources; one per block of the explorer's form."""

    parameter = forms.ModelChoiceField(
        Parameter.objects.filter(pk__in=Variable.objects.values("parameter")),
        label="Parámetro",
        empty_label="Elige un parámetro",
        error_messages={"required": "Elige un parámetro."},
    )
    points = forms.ModelMultipleChoiceField(SamplingPoint.objects.none(), label="Puntos", required=False)
    sources = forms.ModelMultipleChoiceField(
        Source.objects.none(), label="Fuentes", required=False, help_text="Ninguna marcada: todas."
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Choosing a parameter brings its points and sources into this block without reloading the page.
        self.fields["parameter"].widget.attrs.update({
            "hx-get": reverse("explorer_options"),
            "hx-target": f"#opciones-{self.prefix}",
            "hx-vals": json.dumps({"prefix": self.prefix}),
        })
        # Not "parameter": in a template, form.parameter is the field.
        self.chosen = self.find_parameter()
        if self.chosen is not None:
            self.fields["points"].queryset = point_choices(self.chosen)
            self.fields["sources"].queryset = source_choices(self.chosen)

    def find_parameter(self):
        source = self.data if self.is_bound else self.initial
        try:
            pk = int(source.get(self.add_prefix("parameter")) or "")
        except ValueError:
            return None
        return self.fields["parameter"].queryset.filter(pk=pk).first()

    def clean(self):
        data = super().clean()
        points = data.get("points")
        if data.get("parameter") and not points and "points" not in self.errors:
            self.add_error("points", "Elige al menos un punto.")
        elif points and len(points) > MAX_POINTS:
            self.add_error("points", f"Elige hasta {MAX_POINTS} puntos: más colores no se distinguen en una gráfica.")
        if not data.get("sources"):
            data["sources"] = list(self.fields["sources"].queryset)
        return data

    # What the template needs to draw the checkboxes, grouped by zone and keeping the choices.

    @property
    def points_name(self):
        return self.add_prefix("points")

    @property
    def sources_name(self):
        return self.add_prefix("sources")

    def selected_ids(self, name):
        source = self.data if self.is_bound else self.initial
        name = self.add_prefix(name)
        values = source.getlist(name) if hasattr(source, "getlist") else source.get(name, [])
        return {int(pk) for pk in values if str(pk).isdigit()}

    def point_groups(self):
        """[(zone, [(point, checked), …]), …] in the plant's order."""
        chosen = self.selected_ids("points")
        groups = []
        for point in self.fields["points"].queryset:
            zone = point.area.name if point.area else "Sin zona"
            if not groups or groups[-1][0] != zone:
                groups.append((zone, []))
            groups[-1][1].append((point, point.pk in chosen))
        return groups

    def source_options(self):
        chosen = self.selected_ids("sources")
        return [(source, not chosen or source.pk in chosen) for source in self.fields["sources"].queryset]


class ExplorerForm(forms.Form):
    """The dates and the kind of chart, for every parameter, and one block per parameter."""

    start = forms.DateField(label="Desde", required=False, widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"))
    end = forms.DateField(label="Hasta", required=False, widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"))
    aggregation = forms.ChoiceField(label="Gráfica", choices=AGGREGATIONS, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = timezone.localdate()
        self.fields["end"].initial = today
        self.fields["start"].initial = today - datetime.timedelta(days=DEFAULT_DAYS - 1)
        self.fields["aggregation"].initial = AUTO
        # A block added and left on «Elige un parámetro» is ignored; with none chosen, the first
        # block asks for one.
        numbers = [n for n in block_numbers(self.data) if self.data.get(f"p{n}-parameter")] if self.is_bound else []
        self.blocks = [ParameterBlockForm(self.data if self.is_bound else None, prefix=f"p{n}") for n in numbers or [1]]
        self.empty_block = ParameterBlockForm(prefix="p__n__")  # the one «Añadir parámetro» copies

    def is_valid(self):
        for block in self.blocks:  # every block, for its errors
            block.is_valid()
        valid = super().is_valid()  # clean() may still mark a repeated parameter in a block
        return valid and not any(block.errors for block in self.blocks)

    def clean(self):
        data = super().clean()
        seen = set()
        for block in self.blocks:
            if block.chosen is not None and block.chosen.pk in seen:
                block.add_error("parameter", "Ese parámetro ya está en otro bloque: añade ahí sus puntos.")
            elif block.chosen is not None:
                seen.add(block.chosen.pk)
        last_day = data.get("end") or self.fields["end"].initial
        first_day = data.get("start") or last_day - datetime.timedelta(days=DEFAULT_DAYS - 1)
        if first_day > last_day:
            self.add_error("start", "Debe ser anterior a la fecha final.")
        data["start"], data["end"] = first_day, last_day
        data["aggregation"] = data.get("aggregation") or AUTO
        return data

    def selections(self):
        """[(parameter, points, sources), …] of a valid form, one per block, in order."""
        return [(b.cleaned_data["parameter"], list(b.cleaned_data["points"]), b.cleaned_data["sources"]) for b in self.blocks]


def chosen_variables(selections):
    """The variables of each block: its parameter at its points, with its sources."""
    query = Q(pk__in=[])
    for parameter, points, sources in selections:
        query |= Q(parameter=parameter, point__in=points, source__in=sources)
    return list(Variable.objects.filter(query).select_related("point", "source", "parameter"))


@dataclass
class SeriesResult:
    variable: Variable
    color: str  # the point's, as on the chart
    shape: str  # the source's
    description: Description
    exceedance: Exceedance
    suspect: int


@dataclass
class UnitChart:
    """The parameters of one unit: their chart and the statistics of their series."""

    unit: str
    parameters: list
    results: list
    chart: dict

    @property
    def several(self):
        return len(self.parameters) > 1


@dataclass
class Exploration:
    parameters: list
    first_day: datetime.date
    last_day: datetime.date
    variables: list
    samples: dict  # {variable id: [Sample]}
    charts: list  # [UnitChart], one per unit
    period: str | None
    automatic: bool

    @property
    def results(self):
        return [result for chart in self.charts for result in chart.results]

    @property
    def period_name(self):
        return PERIOD_NAMES.get(self.period, "valores sin agregar")


def explore(form):
    """The series and statistics of a valid ExplorerForm."""
    selections = form.selections()
    first_day, last_day, aggregation = form.cleaned_data["start"], form.cleaned_data["end"], form.cleaned_data["aggregation"]
    parameters = [parameter for parameter, _, _ in selections]
    variables = chosen_variables(selections)
    # Each parameter's limits only at its own points.
    limits = Limit.objects.none()
    for parameter, points, _ in selections:
        limits |= Limit.objects.filter(parameter=parameter, point__in=points)
    limits = list(limits.select_related("point", "parameter"))
    books = {parameter.pk: LimitBook([limit for limit in limits if limit.parameter_id == parameter.pk]) for parameter in parameters}
    samples = load_samples(variables, first_day, last_day)
    suspect = count_suspect(variables, first_day, last_day)
    shapes = source_shapes()
    automatic = aggregation == AUTO
    if automatic:
        period = automatic_period(first_day, last_day)
    else:
        period = None if aggregation == RAW else aggregation

    # One chart per unit, in the order of the blocks.
    units = {}
    for parameter, points, _ in selections:
        members, chart_points = units.setdefault(parameter.unit, ([], set()))
        members.append(parameter)
        chart_points.update(point.pk for point in points)
    charts = []
    for unit, (members, chart_points) in units.items():
        # The points of all its parameters, in the plant's order: the color of each.
        points = list(SamplingPoint.objects.filter(pk__in=chart_points))
        colors = {point.pk: point_color(index) for index, point in enumerate(points)}
        order = [parameter.pk for parameter in members]
        series = sorted((v for v in variables if v.parameter_id in order), key=lambda v: order.index(v.parameter_id))
        results = [
            SeriesResult(
                variable=variable,
                color=colors[variable.point_id],
                shape=shapes[variable.source_id][0],
                description=describe(samples.get(variable.pk, [])),
                exceedance=books[variable.parameter_id].exceedance(variable.point_id, samples.get(variable.pk, [])),
                suspect=suspect.get(variable.pk, 0),
            )
            for variable in series
        ]
        chart = chart_data(members, points, series, samples, books, first_day, last_day, period)
        charts.append(UnitChart(unit=unit, parameters=members, results=results, chart=chart))
    return Exploration(
        parameters=parameters,
        first_day=first_day,
        last_day=last_day,
        variables=variables,
        samples=samples,
        charts=charts,
        period=period,
        automatic=automatic,
    )
