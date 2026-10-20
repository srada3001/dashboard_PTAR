"""What a chart receives; static/js/charts.js draws it.

The color tells the point and the marker's shape tells the source (docs/REQUISITOS.md §7.1). Point
colors follow the order the points are given, so hiding a point never repaints the others; each
source keeps its shape on every chart. The colors are the validated categorical order of the
dataviz palette, eight at most.
"""

import calendar
import datetime

from django.utils import timezone

from apps.catalog.models import Source
from apps.measurements.models import TimePrecision
from apps.measurements.values import format_number

from .stats import Period, aggregate

POINT_COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
# (shape for the page's legend, ECharts symbol); the fifth is a triangle pointing down.
SOURCE_SHAPES = [
    ("circle", "circle"), ("triangle", "triangle"), ("diamond", "diamond"), ("square", "rect"),
    ("down", "path://M0,0L10,0L5,10Z"),
]
PRECISION_CODES = {TimePrecision.HOUR: "h", TimePrecision.AM: "a", TimePrecision.PM: "p", TimePrecision.DAY: "d"}


def point_color(index):
    return POINT_COLORS[index % len(POINT_COLORS)]


def source_shapes():
    """{source id: (shape, symbol)}: every source keeps its shape on every chart."""
    return {source.pk: SOURCE_SHAPES[index % len(SOURCE_SHAPES)] for index, source in enumerate(Source.objects.all())}


def epoch(moment):
    """Seconds of Bogotá's wall clock read as UTC. The chart draws in UTC, so it shows Bogotá's
    hours whatever the browser's time zone."""
    if isinstance(moment, datetime.datetime):
        moment = timezone.localtime(moment).replace(tzinfo=None)
    else:
        moment = datetime.datetime.combine(moment, datetime.time(0))
    return calendar.timegm(moment.timetuple())


def bounds_text(low, high, unit=""):
    """'≤ 0,2 mg/L', '≥ 5', '6,4 – 8,5'."""
    unit = f" {unit}" if unit else ""
    if low is None:
        return f"≤ {format_number(high)}{unit}"
    if high is None:
        return f"≥ {format_number(low)}{unit}"
    return f"{format_number(low)} – {format_number(high)}{unit}"


def limit_text(limit, first_day, last_day):
    """'BA-4010 · Límite de vertimiento: ≤ 0,2 mg/L', with its dates when it does not cover the chart."""
    text = f"{limit.point} · {limit.get_kind_display()}: {bounds_text(limit.min_value, limit.max_value, limit.parameter.unit)}"
    if limit.valid_from and limit.valid_from > first_day:
        text += f", desde el {limit.valid_from:%Y-%m-%d}"
    if limit.valid_to and limit.valid_to < last_day:
        text += f", hasta el {limit.valid_to:%Y-%m-%d}"
    return text


def chart_data(parameter, points, variables, samples, limit_book, first_day, last_day, period=None):
    """The chart of a parameter at some points (in color order), from `samples` ({variable id:
    [Sample]}), with the limits in force between the two days. With a period, each series is
    drawn as its daily, weekly or monthly means."""
    color_of = {point.pk: index for index, point in enumerate(points)}
    drawn = [variable for variable in variables if samples.get(variable.pk)]
    sources = [source for source in Source.objects.all() if any(v.source_id == source.pk for v in drawn)]
    shape_of = source_shapes()
    source_index = {source.pk: index for index, source in enumerate(sources)}

    series = []
    for variable in drawn:
        rows = samples[variable.pk]
        if period:
            data = [[epoch(bucket.start), bucket.mean, bucket.n, bucket.qualified] for bucket in aggregate(rows, period)]
        else:
            data = [[epoch(s.taken_at), s.value, s.qualifier, PRECISION_CODES[s.precision]] for s in rows]
        series.append({
            "name": f"{variable.point} · {variable.source}",
            "point": color_of[variable.point_id],
            "source": source_index[variable.source_id],
            "data": data,
        })

    limits = []
    for point in points:
        for limit in limit_book.overlapping(point.pk, first_day, last_day):
            start = max(limit.valid_from or first_day, first_day)
            end = min(limit.valid_to or last_day, last_day) + datetime.timedelta(days=1)
            limits.append({
                "point": color_of[point.pk],
                "color": point_color(color_of[point.pk]),
                "text": limit_text(limit, first_day, last_day),
                "values": [value for value in (limit.min_value, limit.max_value) if value is not None],
                "from": epoch(start),
                "to": epoch(end),
            })

    with_data = {variable.point_id for variable in drawn}
    qualified = any(sample.qualifier for rows in samples.values() for sample in rows)
    return {
        "unit": parameter.unit,
        "decimals": parameter.decimals,
        "start": epoch(first_day),
        "end": epoch(last_day + datetime.timedelta(days=1)),
        "period": period,
        # A missing bucket breaks the line; raw series are broken by charts.js from their own rhythm.
        "gap": Period.LENGTH[period].total_seconds() * 1.5 if period else None,
        "qualified": qualified,
        "points": [
            {"code": point.code, "color": point_color(color_of[point.pk]), "hasData": point.pk in with_data}
            for point in points
        ],
        "sources": [
            {"code": source.code, "shape": shape_of[source.pk][0], "symbol": shape_of[source.pk][1]} for source in sources
        ],
        "series": series,
        "limits": limits,
    }
