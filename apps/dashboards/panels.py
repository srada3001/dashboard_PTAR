"""The cards of «Variables importantes» (docs/REQUISITOS.md §7.1).

Each card is a list of chosen variables (point + parameter + source, the same unit), up to a day
(today by default): the chart of the last days, and per series the last value, the minimum and maximum of the
last 7 days, the means of the last 7 and 30 days, and how many of the last 7 days' samples broke
the limit in force on their date.
"""

from dataclasses import dataclass, field

from apps.catalog.models import Limit, Variable

from .charts import chart_data, image, point_color, source_shapes
from .models import ImportantVariable
from .stats import (
    Description,
    Exceedance,
    LimitBook,
    Period,
    Sample,
    describe,
    last_days,
    latest_sample,
    load_samples,
    within,
)

CHART_DAYS = (7, 30, 90, 365)
DEFAULT_CHART_DAYS = 30
# From this many days, the chart shows daily means: hourly values would be too many to read.
DAILY_MEANS_FROM = 90


@dataclass
class Row:
    variable: Variable
    color: str  # the point's, as on the chart
    shape: str  # the source's
    latest: Sample
    latest_breaks: bool | None  # None: no limit in force on its date
    week: Description
    month: Description
    week_exceedance: Exceedance


@dataclass
class Card:
    item: ImportantVariable
    rows: list = field(default_factory=list)
    # Series with nothing in the chart nor in the last 30 days: (variable, last value or None).
    stale: list = field(default_factory=list)
    chart: dict | None = None
    image: tuple = ("", "")  # (file name, title) of the chart downloaded as a PNG

    parameters: list = field(default_factory=list)

    @property
    def unit(self):
        return self.parameters[0].unit if self.parameters else ""

    @property
    def codes(self):
        """"SST, SS": the parameters of the card, when they are not already its title."""
        codes = ", ".join(parameter.code for parameter in self.parameters)
        return "" if codes == self.item.title else codes

    @property
    def chart_id(self):
        return f"grafica-{self.item.pk}"


def unique(items):
    return list(dict.fromkeys(items))


def build_card(item, last_day, chart_days):
    card = Card(item)
    variables = [entry.variable for entry in item.items.all()]
    if not variables:
        return card
    points = unique(variable.point for variable in variables)
    parameters = card.parameters = unique(variable.parameter for variable in variables)
    limits = Limit.objects.filter(parameter__in=parameters, point__in=points).select_related("point", "parameter")
    books = {parameter.pk: LimitBook([limit for limit in limits if limit.parameter_id == parameter.pk]) for parameter in parameters}

    chart_first = last_days(last_day, chart_days)
    month_first, week_first = last_days(last_day, 30), last_days(last_day, 7)
    samples = load_samples(variables, min(chart_first, month_first), last_day)

    colors = {point.pk: point_color(index) for index, point in enumerate(points)}
    shapes = source_shapes()
    chart_samples = {}
    for variable in variables:
        loaded = samples.get(variable.pk, [])
        chart_samples[variable.pk] = within(loaded, chart_first, last_day)
        month = within(loaded, month_first, last_day)
        if not month and not chart_samples[variable.pk]:
            card.stale.append((variable, latest_sample(variable, last_day)))
            continue
        # Loaded up to the end of the last day, so the newest loaded value is the last one there is.
        latest = loaded[-1]
        week = within(month, week_first, last_day)
        book = books[variable.parameter_id]
        card.rows.append(Row(
            variable=variable,
            color=colors[variable.point_id],
            shape=shapes[variable.source_id][0],
            latest=latest,
            latest_breaks=book.breaks(variable.point_id, latest),
            week=describe(week),
            month=describe(month),
            week_exceedance=book.exceedance(variable.point_id, week),
        ))

    period = Period.DAY if chart_days >= DAILY_MEANS_FROM else None
    card.chart = chart_data(parameters, points, variables, chart_samples, books, chart_first, last_day, period)
    card.image = image(item.title, card.unit, chart_first, last_day)
    return card


def build_cards(last_day, chart_days):
    items = ImportantVariable.objects.prefetch_related("items__variable__point", "items__variable__parameter", "items__variable__source")
    return [build_card(item, last_day, chart_days) for item in items]
