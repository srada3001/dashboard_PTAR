"""Sampling times of the rows of a table (docs/REQUISITOS.md §9).

Hourly tables (table 1) have one row per hour, written by hand or by dragging, so they carry
drift (06:59:59.65 instead of 07:00) and typos (a wrong day or month, on one row or on a whole
stretch, or one date repeated). Hours are rounded, and rows whose hours break the sequence are
fixed only when their neighbours leave no doubt: n rows between two hours n + 1 hours apart.
Rows that cannot be fixed keep the hour written, so a wrong hour that falls on another row's
hour becomes a duplicate and is handled as one. Dates before 2000 or in the future are never
taken as written. Daily tables only keep the day.
"""

import datetime
from dataclasses import dataclass, field

HOUR = datetime.timedelta(hours=1)
FIRST_YEAR = 2000


@dataclass
class RowTime:
    when: object = None  # datetime (hourly tables) or date (daily tables); None: the row is not imported
    written: object = None
    deduced: bool = False
    rounded: bool = False
    reason: str = ""  # why the row is not imported


@dataclass
class Timeline:
    rows: list = field(default_factory=list)  # RowTime per row, same order as the table

    @property
    def deduced(self):
        return [row for row in self.rows if row.deduced]

    @property
    def dropped(self):
        return [row for row in self.rows if row.when is None]


def round_to_hour(moment):
    return (moment + datetime.timedelta(minutes=30)).replace(minute=0, second=0, microsecond=0)


def is_date(value):
    return isinstance(value, (datetime.datetime, datetime.date))


def unusable_reason(written, moment, now):
    """Why a written date cannot be taken as is, or "" when it can."""
    if written in (None, ""):
        return "Sin fecha."
    if moment is None:
        return "Fecha no válida."
    if moment.year < FIRST_YEAR:
        return "Fecha imposible."
    if moment > now:
        return "Fecha futura."
    return ""


def daily_timeline(written_dates, today):
    """One date per row, without its time."""
    timeline = Timeline()
    for written in written_dates:
        day = None
        if is_date(written):
            day = written.date() if isinstance(written, datetime.datetime) else written
        reason = unusable_reason(written, day, today)
        timeline.rows.append(RowTime(when=None if reason else day, written=written, reason=reason))
    return timeline


def segments_of(rounded, usable):
    """Maximal stretches of usable rows one hour apart, as (first, last) row indexes."""
    segments, i = [], 0
    while i < len(rounded):
        j = i
        if usable[i]:
            while j + 1 < len(rounded) and usable[j + 1] and rounded[j + 1] - rounded[j] == HOUR:
                j += 1
        segments.append((i, j))
        i = j + 1
    return segments


def hourly_timeline(written_times, now):
    """One hour per row (naive local times), deduced from the sequence where the written one is wrong."""
    count = len(written_times)
    rounded = [round_to_hour(w) if isinstance(w, datetime.datetime) else None for w in written_times]
    reasons = [unusable_reason(written_times[i], rounded[i], now) for i in range(count)]
    usable = [not reason for reason in reasons]

    times = [rounded[i] if usable[i] else None for i in range(count)]
    deduced = [False] * count

    def fits(before, after):
        """The rows between two anchor rows fill the hours between them exactly."""
        return rounded[after] - rounded[before] == (after - before) * HOUR

    def deduce(before, after):
        for j in range(before + 1, after):
            times[j] = rounded[before] + (j - before) * HOUR
            deduced[j] = times[j] != rounded[j]
            reasons[j] = ""

    # Rows are anchored when they belong to a stretch of at least two consecutive hours. The
    # rows between two anchored stretches are deduced when they fit exactly between them.
    segments = [(first, last) for first, last in segments_of(rounded, usable) if last > first]
    for (_, end), (start, _) in zip(segments, segments[1:]):
        if start - end > 1 and fits(end, start):
            deduce(end, start)

    # A whole stretch can be out of place too (a wrong day or month dragged along it): its
    # neighbours agree with each other but not with it. It is deduced the same way, when
    # everything between the neighbours fits exactly; otherwise it stays as written.
    for previous, (first, last), following in zip(segments, segments[1:], segments[2:]):
        previous_end, next_start = previous[1], following[0]
        out_of_place = not (rounded[previous_end] < rounded[first] and rounded[last] < rounded[next_start])
        if rounded[previous_end] < rounded[next_start] and out_of_place and fits(previous_end, next_start):
            deduce(previous_end, next_start)

    timeline = Timeline()
    for j in range(count):
        when = times[j]
        timeline.rows.append(RowTime(
            when=when,
            written=written_times[j],
            deduced=deduced[j],
            rounded=when is not None and not deduced[j] and written_times[j] != when,
            reason="" if when is not None else reasons[j],
        ))
    return timeline
