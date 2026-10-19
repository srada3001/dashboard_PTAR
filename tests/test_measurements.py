"""What a value may be, and how measurements and their history are kept (docs/REQUISITOS.md §5–§6)."""

import datetime

import pytest
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.measurements.models import (
    Measurement,
    MeasurementHistory,
    Origin,
    TimePrecision,
    format_taken_at,
    period_start,
)
from apps.measurements.values import (
    InvalidValue,
    format_number,
    outside_physical_range,
    outside_typical_range,
    parse_value,
)


class TestParseValue:
    @pytest.mark.parametrize(
        ("text", "qualifier", "value"),
        [
            ("7,4", "", 7.4),
            ("7.4", "", 7.4),
            ("  12 ", "", 12.0),
            ("<0,1", "<", 0.1),
            ("< 0,1", "<", 0.1),
            ("> 500", ">", 500.0),
            ("<10", "<", 10.0),
            ("-332", "", -332.0),
            (",5", "", 0.5),
        ],
    )
    def test_numbers_with_comma_or_point_and_an_optional_qualifier(self, text, qualifier, value):
        parsed = parse_value(text)
        assert (parsed.qualifier, parsed.value) == (qualifier, value)

    @pytest.mark.parametrize("text", ["7,,4", "7/4", "19+", "6,8/", "ND", "SB", "asdfdf", "", "1.234,5", "<", "7,4 mg"])
    def test_anything_else_is_not_a_value(self, text):
        with pytest.raises(InvalidValue):
            parse_value(text)


class TestRanges:
    class Bounds:
        def __init__(self, low=None, high=None):
            self.physical_min = self.typical_min = low
            self.physical_max = self.typical_max = high

    def test_without_a_range_every_number_is_valid(self):
        assert not outside_physical_range(self.Bounds(), 4900)
        assert not outside_typical_range(self.Bounds(), -1)

    def test_physical_range(self):
        ph = self.Bounds(0, 14)
        assert outside_physical_range(ph, 73)
        assert outside_physical_range(ph, -0.1)
        assert not outside_physical_range(ph, 14)

    def test_one_sided_range(self):
        sst = self.Bounds(low=0)
        assert outside_physical_range(sst, -332)
        assert not outside_physical_range(sst, 32380)


def test_numbers_are_shown_with_a_decimal_comma():
    assert format_number(7.3) == "7,3"
    assert format_number(10.0) == "10"
    assert format_number(0.027) == "0,027"
    assert format_number(1.8e9) == "1800000000"
    assert format_number(7.3, 2) == "7,30"


class TestSamplingTime:
    def test_periods_start_at_midnight_or_noon(self):
        day = datetime.date(2024, 1, 3)
        assert timezone.localtime(period_start(day, TimePrecision.DAY)).hour == 0
        assert timezone.localtime(period_start(day, TimePrecision.AM)).hour == 0
        assert timezone.localtime(period_start(day, TimePrecision.PM)).hour == 12

    def test_no_hour_is_shown_when_it_is_not_known(self):
        taken_at = period_start(datetime.date(2024, 1, 3), TimePrecision.PM)
        assert format_taken_at(taken_at, TimePrecision.PM) == "2024-01-03 p. m."
        assert format_taken_at(taken_at, TimePrecision.DAY) == "2024-01-03"
        assert format_taken_at(taken_at, TimePrecision.HOUR) == "2024-01-03 12:00"


@pytest.mark.django_db
class TestMeasurement:
    def make(self, variable, user, **fields):
        values = {
            "variable": variable, "taken_at": period_start(datetime.date(2024, 1, 3), TimePrecision.DAY),
            "time_precision": TimePrecision.DAY, "value": 0.2, "origin": Origin.HISTORY, "created_by": user,
        }
        values.update(fields)
        return Measurement.objects.create(**values)

    def test_one_value_per_variable_and_time(self, phenols_biota, admin_user):
        self.make(phenols_biota, admin_user)
        with pytest.raises(IntegrityError), transaction.atomic():
            self.make(phenols_biota, admin_user, value=0.3)

    def test_the_qualifier_is_shown_with_the_value(self, phenols_biota, admin_user):
        assert self.make(phenols_biota, admin_user, qualifier="<", value=0.1).display_value == "<0,1"

    def test_the_history_is_never_deleted(self, phenols_biota, admin_user):
        measurement = self.make(phenols_biota, admin_user)
        entry = MeasurementHistory.objects.create(
            measurement=measurement, variable=phenols_biota, taken_at=measurement.taken_at,
            time_precision=measurement.time_precision, action=MeasurementHistory.Action.CREATE,
            new_value=0.2, user=admin_user,
        )
        with pytest.raises(PermissionError):
            entry.delete()
        with pytest.raises(PermissionError):
            MeasurementHistory.objects.all().delete()
        measurement.delete()
        entry.refresh_from_db()
        assert entry.measurement is None
        assert entry.change == "— → 0,2"
