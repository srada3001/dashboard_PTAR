"""The series explorer (docs/REQUISITOS.md §7.2): a parameter at one or more points and sources,
between two dates, with descriptive statistics per series.

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


def point_choices(parameter):
    return SamplingPoint.objects.filter(pk__in=Variable.objects.filter(parameter=parameter).values("point")).select_related("area")


def source_choices(parameter):
    return Source.objects.filter(pk__in=Variable.objects.filter(parameter=parameter).values("source"))


class ExplorerForm(forms.Form):
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
    start = forms.DateField(label="Desde", required=False, widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"))
    end = forms.DateField(label="Hasta", required=False, widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"))
    aggregation = forms.ChoiceField(label="Gráfica", choices=AGGREGATIONS, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = timezone.localdate()
        self.fields["end"].initial = today
        self.fields["start"].initial = today - datetime.timedelta(days=DEFAULT_DAYS - 1)
        self.fields["aggregation"].initial = AUTO
        # Choosing a parameter brings its points and sources without reloading the page.
        self.fields["parameter"].widget.attrs.update({"hx-get": reverse("explorer_options"), "hx-target": "#opciones"})
        # Not "parameter": in a template, form.parameter is the field.
        self.chosen = self.find_parameter()
        if self.chosen is not None:
            self.fields["points"].queryset = point_choices(self.chosen)
            self.fields["sources"].queryset = source_choices(self.chosen)

    def find_parameter(self):
        try:
            pk = int(self.data.get("parameter") or self.initial.get("parameter") or "")
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
        last_day = data.get("end") or self.fields["end"].initial
        first_day = data.get("start") or last_day - datetime.timedelta(days=DEFAULT_DAYS - 1)
        if first_day > last_day:
            self.add_error("start", "Debe ser anterior a la fecha final.")
        data["start"], data["end"] = first_day, last_day
        data["aggregation"] = data.get("aggregation") or AUTO
        return data

    # What the template needs to draw the checkboxes, grouped by zone and keeping the choices.

    def selected_ids(self, name):
        if not self.is_bound:
            return set()
        values = self.data.getlist(name) if hasattr(self.data, "getlist") else self.data.get(name, [])
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


@dataclass
class SeriesResult:
    variable: Variable
    color: str  # the point's, as on the chart
    shape: str  # the source's
    description: Description
    exceedance: Exceedance
    suspect: int


@dataclass
class Exploration:
    parameter: Parameter
    first_day: datetime.date
    last_day: datetime.date
    variables: list
    samples: dict  # {variable id: [Sample]}
    results: list
    chart: dict
    period: str | None
    automatic: bool

    @property
    def period_name(self):
        return PERIOD_NAMES.get(self.period, "valores sin agregar")


def explore(data):
    """The series and statistics of a valid ExplorerForm's cleaned_data."""
    parameter, first_day, last_day = data["parameter"], data["start"], data["end"]
    points = list(data["points"])  # in the plant's order: the queryset keeps the points' ordering
    variables = list(
        Variable.objects.filter(parameter=parameter, point__in=points, source__in=data["sources"]).select_related("point", "source")
    )
    book = LimitBook(Limit.objects.filter(parameter=parameter, point__in=points).select_related("point", "parameter"))
    samples = load_samples(variables, first_day, last_day)
    suspect = count_suspect(variables, first_day, last_day)
    colors = {point.pk: point_color(index) for index, point in enumerate(points)}
    shapes = source_shapes()
    results = [
        SeriesResult(
            variable=variable,
            color=colors[variable.point_id],
            shape=shapes[variable.source_id][0],
            description=describe(samples.get(variable.pk, [])),
            exceedance=book.exceedance(variable.point_id, samples.get(variable.pk, [])),
            suspect=suspect.get(variable.pk, 0),
        )
        for variable in variables
    ]
    automatic = data["aggregation"] == AUTO
    if automatic:
        period = automatic_period(first_day, last_day)
    else:
        period = None if data["aggregation"] == RAW else data["aggregation"]
    return Exploration(
        parameter=parameter,
        first_day=first_day,
        last_day=last_day,
        variables=variables,
        samples=samples,
        results=results,
        chart=chart_data(parameter, points, variables, samples, book, first_day, last_day, period),
        period=period,
        automatic=automatic,
    )
