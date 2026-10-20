"""Samples, windows, descriptive statistics and limit checks for the views (docs/REQUISITOS.md §7, §8).

- Suspect values never get here: the queries leave them out until someone reviews them.
- A value with a qualifier counts as its number, the worst case: "<0,1" as 0.1 and ">500" as 500.
- A value that does not exist has no row, so it leaves a gap; no samples is "sin datos", never "cumple".
- Windows are calendar days in Bogotá: "the last 7 days" up to the 19th are the 13th to the 19th,
  whatever the hour, so a sample known only by its day counts in the day it belongs to.
"""

import datetime
import math
import statistics
from collections import defaultdict
from dataclasses import dataclass

from django.utils import timezone

from apps.measurements.models import Measurement
from apps.measurements.values import outside


@dataclass(frozen=True)
class Sample:
    taken_at: datetime.datetime  # aware; the start of the period when the hour is not known
    precision: str  # TimePrecision
    value: float
    qualifier: str  # "", "<" or ">"

    @property
    def local(self):
        return timezone.localtime(self.taken_at)

    @property
    def day(self):
        return self.local.date()


def day_span(first_day, last_day):
    """The instants of a range of calendar days: [first day 00:00, day after the last 00:00)."""
    start = timezone.make_aware(datetime.datetime.combine(first_day, datetime.time(0)))
    end = timezone.make_aware(datetime.datetime.combine(last_day + datetime.timedelta(days=1), datetime.time(0)))
    return start, end


def last_days(last_day, count):
    """The first day of the `count` calendar days that end on `last_day`."""
    return last_day - datetime.timedelta(days=count - 1)


def valid_measurements(variables):
    return Measurement.objects.filter(variable__in=variables, suspect=False)


def load_samples(variables, first_day, last_day):
    """{variable id: [Sample, …] in time order} for the days asked, without suspect values."""
    start, end = day_span(first_day, last_day)
    rows = (
        valid_measurements(variables)
        .filter(taken_at__gte=start, taken_at__lt=end)
        .order_by("variable_id", "taken_at")
        .values_list("variable_id", "taken_at", "time_precision", "value", "qualifier")
    )
    samples = defaultdict(list)
    for variable_id, taken_at, precision, value, qualifier in rows.iterator(chunk_size=5000):
        samples[variable_id].append(Sample(taken_at, precision, value, qualifier))
    return samples


def count_suspect(variables, first_day, last_day):
    """{variable id: suspect values in those days}, left out of the charts and the statistics."""
    start, end = day_span(first_day, last_day)
    rows = (
        Measurement.objects.filter(variable__in=variables, suspect=True, taken_at__gte=start, taken_at__lt=end)
        .values_list("variable_id", flat=True)
    )
    counts = defaultdict(int)
    for variable_id in rows:
        counts[variable_id] += 1
    return counts


def latest_sample(variable, last_day):
    """The last valid value up to the end of `last_day`, however old, or None."""
    _, end = day_span(last_day, last_day)
    row = (
        valid_measurements([variable])
        .filter(taken_at__lt=end)
        .order_by("-taken_at")
        .values_list("taken_at", "time_precision", "value", "qualifier")
        .first()
    )
    return Sample(*row) if row else None


def within(samples, first_day, last_day):
    return [sample for sample in samples if first_day <= sample.day <= last_day]


# ---------------------------------------------------------------- descriptive statistics


@dataclass(frozen=True)
class Description:
    n: int
    mean: float | None = None
    median: float | None = None
    minimum: float | None = None
    maximum: float | None = None
    std: float | None = None  # sample standard deviation (STDEV.S in Excel); needs two values
    p10: float | None = None
    p90: float | None = None


def percentile(ordered, fraction):
    """Linear interpolation between the closest ranks, as Excel's PERCENTILE.INC does."""
    position = (len(ordered) - 1) * fraction
    low, high = math.floor(position), math.ceil(position)
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


def describe(samples):
    values = sorted(sample.value for sample in samples)
    if not values:
        return Description(n=0)
    return Description(
        n=len(values),
        mean=statistics.fmean(values),
        median=statistics.median(values),
        minimum=values[0],
        maximum=values[-1],
        std=statistics.stdev(values) if len(values) > 1 else None,
        p10=percentile(values, 0.1),
        p90=percentile(values, 0.9),
    )


# ---------------------------------------------------------------- limits


@dataclass(frozen=True)
class Exceedance:
    """How many samples broke the limit in force on their date, out of those that had one."""

    out: int
    checked: int
    total: int

    @property
    def percent(self):
        return 100 * self.out / self.checked if self.checked else None


class LimitBook:
    """The limits of one parameter at some points, each with its validity. A sample is checked
    against every limit in force on its date at its point, whatever its kind; it breaks the
    limits when it falls outside any of them."""

    def __init__(self, limits):
        self.by_point = defaultdict(list)
        for limit in limits:
            self.by_point[limit.point_id].append(limit)

    def in_force(self, point_id, day):
        return [
            limit for limit in self.by_point[point_id]
            if (limit.valid_from is None or limit.valid_from <= day) and (limit.valid_to is None or day <= limit.valid_to)
        ]

    def overlapping(self, point_id, first_day, last_day):
        return [
            limit for limit in self.by_point[point_id]
            if (limit.valid_from is None or limit.valid_from <= last_day) and (limit.valid_to is None or first_day <= limit.valid_to)
        ]

    def breaks(self, point_id, sample):
        """True or False, or None when no limit is in force on the sample's date."""
        limits = self.in_force(point_id, sample.day)
        if not limits:
            return None
        return any(outside(sample.value, limit.min_value, limit.max_value) for limit in limits)

    def exceedance(self, point_id, samples):
        out = checked = 0
        for sample in samples:
            result = self.breaks(point_id, sample)
            if result is not None:
                checked += 1
                out += result
        return Exceedance(out=out, checked=checked, total=len(samples))


# ---------------------------------------------------------------- aggregation


class Period:
    DAY = "day"
    WEEK = "week"
    MONTH = "month"

    LENGTH = {DAY: datetime.timedelta(days=1), WEEK: datetime.timedelta(days=7), MONTH: datetime.timedelta(days=31)}


def period_start(day, period):
    if period == Period.WEEK:
        return day - datetime.timedelta(days=day.weekday())  # weeks start on Monday
    if period == Period.MONTH:
        return day.replace(day=1)
    return day


@dataclass(frozen=True)
class Bucket:
    start: datetime.date
    mean: float
    n: int
    qualified: int  # values with "<" or ">" in the mean


def aggregate(samples, period):
    """The mean of each day, week or month that has samples; the ones without leave a gap."""
    groups = defaultdict(list)
    for sample in samples:
        groups[period_start(sample.day, period)].append(sample)
    return [
        Bucket(
            start=start,
            mean=statistics.fmean(sample.value for sample in group),
            n=len(group),
            qualified=sum(1 for sample in group if sample.qualifier),
        )
        for start, group in sorted(groups.items())
    ]
