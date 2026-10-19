"""Sampling times of the historical rows (docs/REQUISITOS.md §9): rounding, deduction by the
sequence, and dates that are never taken as written. The cases come from «Entrada de Datos»."""

import datetime

from apps.imports.timeline import daily_timeline, hourly_timeline

NOW = datetime.datetime(2026, 10, 18, 12)
H = datetime.timedelta(hours=1)


def hours(start, count):
    return [start + i * H for i in range(count)]


def whens(timeline):
    return [row.when for row in timeline.rows]


def test_drifting_hours_are_rounded():
    written = [datetime.datetime(2024, 1, 3, 5, 59, 59, 660000), datetime.datetime(2024, 1, 3, 6, 59, 59, 650000),
               datetime.datetime(2024, 1, 3, 8, 0, 0, 20000)]
    timeline = hourly_timeline(written, NOW)
    assert whens(timeline) == hours(datetime.datetime(2024, 1, 3, 6), 3)
    assert all(row.rounded and not row.deduced for row in timeline.rows)


def test_a_wrong_day_between_two_hours_is_deduced():
    # Row 937: "2022-07-12 15:59" between "2022-07-11 16:00" and "18:00".
    start = datetime.datetime(2022, 7, 11, 14)
    written = hours(start, 3) + [datetime.datetime(2022, 7, 12, 15, 59, 59)] + hours(start + 4 * H, 3)
    timeline = hourly_timeline(written, NOW)
    assert whens(timeline) == hours(start, 7)
    assert [row.deduced for row in timeline.rows] == [False, False, False, True, False, False, False]


def test_a_repeated_date_is_deduced_when_the_rows_fill_the_gap():
    # «2024-12-26 00:00» written on 22 rows that stand for 01:00 to 22:00.
    start = datetime.datetime(2024, 12, 25, 22)
    written = hours(start, 3) + [datetime.datetime(2024, 12, 26)] * 22 + hours(datetime.datetime(2024, 12, 26, 23), 3)
    assert whens(hourly_timeline(written, NOW)) == hours(start, 28)


def test_a_whole_stretch_with_the_wrong_month_is_deduced():
    # Rows 22351–22384: "2025-01-20 11:00" onwards between "2024-12-20 10:00" and "2024-12-21 21:00".
    start = datetime.datetime(2024, 12, 20, 8)
    written = hours(start, 3) + hours(datetime.datetime(2025, 1, 20, 11), 34) + hours(datetime.datetime(2024, 12, 21, 21), 3)
    timeline = hourly_timeline(written, NOW)
    assert whens(timeline) == hours(start, 40)
    assert sum(row.deduced for row in timeline.rows) == 34


def test_an_impossible_year_is_deduced_when_the_neighbours_fix_it():
    start = datetime.datetime(2026, 2, 13, 9)
    written = hours(start, 2) + [datetime.datetime(1903, 3, 3, 11), datetime.datetime(1903, 2, 17, 12)] + hours(start + 4 * H, 2)
    assert whens(hourly_timeline(written, NOW)) == hours(start, 6)


def test_an_impossible_year_that_cannot_be_deduced_is_dropped():
    written = hours(datetime.datetime(2026, 2, 13, 9), 2) + [datetime.datetime(1903, 3, 3, 11)] + hours(datetime.datetime(2026, 2, 14), 2)
    row = hourly_timeline(written, NOW).rows[2]
    assert row.when is None
    assert row.reason == "Fecha imposible."


def test_future_rows_are_dropped():
    written = hours(datetime.datetime(2026, 10, 18, 10), 6)
    timeline = hourly_timeline(written, NOW)
    assert whens(timeline)[:3] == hours(datetime.datetime(2026, 10, 18, 10), 3)
    assert whens(timeline)[3:] == [None, None, None]
    assert timeline.rows[3].reason == "Fecha futura."


def test_an_ambiguous_repeated_day_is_kept_as_written():
    # 2025-12-05: 27 hours typed twice; nothing tells which copy is right, so both keep their
    # hours and become duplicates (which are not imported when their values differ).
    first = hours(datetime.datetime(2025, 12, 5, 0), 32)
    again = hours(datetime.datetime(2025, 12, 5, 5), 40)
    timeline = hourly_timeline(first + again, NOW)
    assert whens(timeline) == first + again
    assert not any(row.deduced for row in timeline.rows)


def test_a_gap_in_the_hours_is_not_filled():
    written = hours(datetime.datetime(2025, 12, 2, 16), 3) + hours(datetime.datetime(2025, 12, 2, 22), 3)
    assert whens(hourly_timeline(written, NOW)) == written


def test_daily_tables_keep_only_the_day():
    written = [datetime.datetime(2023, 1, 1), datetime.datetime(1900, 1, 16, 0, 14, 24), datetime.datetime(2026, 10, 19),
               None, "ayer"]
    timeline = daily_timeline(written, NOW.date())
    assert whens(timeline) == [datetime.date(2023, 1, 1), None, None, None, None]
    assert [row.reason for row in timeline.rows] == ["", "Fecha imposible.", "Fecha futura.", "Sin fecha.", "Fecha no válida."]
