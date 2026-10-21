"""The series explorer (docs/REQUISITOS.md §7.2): one or more parameters at one or more points and
sources, between two dates, with descriptive statistics per series. Parameters with the same unit
share a chart.

The statistics always use the measurements themselves; the daily, weekly or monthly aggregation
only changes what the chart draws, so long series stay readable.
"""

import datetime
from dataclasses import dataclass

from django import forms
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


def point_choices(parameters):
    """The points that measure any of the parameters."""
    return SamplingPoint.objects.filter(pk__in=Variable.objects.filter(parameter__in=parameters).values("point")).select_related("area")


def source_choices(parameters):
    return Source.objects.filter(pk__in=Variable.objects.filter(parameter__in=parameters).values("source"))


class ExplorerForm(forms.Form):
    parameters = forms.ModelMultipleChoiceField(
        Parameter.objects.filter(pk__in=Variable.objects.values("parameter")),
        label="Parámetros",
        error_messages={"required": "Elige al menos un parámetro."},
    )
    points = forms.ModelMultipleChoiceField(SamplingPoint.objects.none(), label="Puntos", required=False)
    sources = forms.ModelMultipleChoiceField(
        Source.objects.none(), label="Fuentes", required=False, help_text="Ninguna marcada: todas."
    )
    start = forms.DateField(label="Desde", required=False, widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"))
    end = forms.DateField(label="Hasta", required=False, widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"))
    aggregation = forms.ChoiceField(label="Gráfica", choices=AGGREGATIONS, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.is_bound and hasattr(self.data, "getlist"):
            # A list added and left on «Elige un parámetro» is not an error: it is ignored.
            self.data = self.data.copy()
            self.data.setlist("parameters", [pk for pk in self.data.getlist("parameters") if pk])
        today = timezone.localdate()
        self.fields["end"].initial = today
        self.fields["start"].initial = today - datetime.timedelta(days=DEFAULT_DAYS - 1)
        self.fields["aggregation"].initial = AUTO
        # Choosing the parameters brings their points and sources without reloading the page.
        self.options_url = reverse("explorer_options")
        # Not "parameters": in a template, form.parameters is the field. In the order they were chosen.
        order = self.ordered_ids("parameters")
        self.chosen = sorted(self.fields["parameters"].queryset.filter(pk__in=order), key=lambda p: order.index(p.pk))
        if self.chosen:
            self.fields["points"].queryset = point_choices(self.chosen)
            self.fields["sources"].queryset = source_choices(self.chosen)

    def clean(self):
        data = super().clean()
        points = data.get("points")
        if data.get("parameters") and not points and "points" not in self.errors:
            self.add_error("points", "Elige al menos un punto.")
        elif points and len(points) > MAX_POINTS:
            self.add_error("points", f"Elige hasta {MAX_POINTS} puntos: más colores no se distinguen en una gráfica.")
        if data.get("parameters"):
            data["parameters"] = self.chosen
        if not data.get("sources"):
            data["sources"] = list(self.fields["sources"].queryset)
        last_day = data.get("end") or self.fields["end"].initial
        first_day = data.get("start") or last_day - datetime.timedelta(days=DEFAULT_DAYS - 1)
        if first_day > last_day:
            self.add_error("start", "Debe ser anterior a la fecha final.")
        data["start"], data["end"] = first_day, last_day
        data["aggregation"] = data.get("aggregation") or AUTO
        return data

    # What the template needs to draw the lists and checkboxes, keeping the choices.

    def ordered_ids(self, name):
        """The ids chosen in the request, or in `initial` (the options brought by HTMX), in order and
        without repeats."""
        source = self.data if self.is_bound else self.initial
        values = source.getlist(name) if hasattr(source, "getlist") else source.get(name, [])
        return list(dict.fromkeys(int(pk) for pk in values if str(pk).isdigit()))

    def selected_ids(self, name):
        return set(self.ordered_ids(name))

    def parameter_rows(self):
        """One list per chosen parameter (its id), or a single empty one."""
        return [parameter.pk for parameter in self.chosen] or [None]

    def parameter_list(self):
        return list(self.fields["parameters"].queryset)

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


def explore(data):
    """The series and statistics of a valid ExplorerForm's cleaned_data."""
    parameters, first_day, last_day = list(data["parameters"]), data["start"], data["end"]
    points = list(data["points"])  # in the plant's order: the queryset keeps the points' ordering
    variables = list(
        Variable.objects.filter(parameter__in=parameters, point__in=points, source__in=data["sources"])
        .select_related("point", "source", "parameter")
    )
    limits = Limit.objects.filter(parameter__in=parameters, point__in=points).select_related("point", "parameter")
    books = {parameter.pk: LimitBook([limit for limit in limits if limit.parameter_id == parameter.pk]) for parameter in parameters}
    samples = load_samples(variables, first_day, last_day)
    suspect = count_suspect(variables, first_day, last_day)
    colors = {point.pk: point_color(index) for index, point in enumerate(points)}
    shapes = source_shapes()
    automatic = data["aggregation"] == AUTO
    if automatic:
        period = automatic_period(first_day, last_day)
    else:
        period = None if data["aggregation"] == RAW else data["aggregation"]

    # One chart per unit, in the order the parameters come in.
    units = {}
    for parameter in parameters:
        units.setdefault(parameter.unit, []).append(parameter)
    charts = []
    for unit, members in units.items():
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
