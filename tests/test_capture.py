"""Manual capture (docs/REQUISITOS.md §4 and §6): cells by frequency, validation on the server,
confirmations, corrections with history, conflicts and who may change what."""

import datetime
import importlib

import pytest
from django.apps import apps as django_apps
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import User
from apps.capture.grid import SLOTS, build, slots_of
from apps.catalog.models import CaptureForm, CaptureFormVariable, Parameter, SamplingPoint, Schedule, Source, Variable
from apps.measurements.models import Measurement, MeasurementHistory, Origin, TimePrecision, period_start
from apps.measurements.records import version

from .conftest import make_client

pytestmark = pytest.mark.django_db

YESTERDAY = timezone.localdate() - datetime.timedelta(days=1)


def at(day, hour):
    return timezone.make_aware(datetime.datetime.combine(day, datetime.time(hour)))


@pytest.fixture
def entry(db):
    return SamplingPoint.objects.create(code="BA-4001", name="Entrada a la PTAR")


@pytest.fixture
def ph_nalco(entry, ph, nalco):
    return Variable.objects.create(point=entry, parameter=ph, source=nalco, time_resolution=Schedule.HOURLY,
                                   typical_min=6, typical_max=9)


@pytest.fixture
def temperature_nalco(entry, nalco):
    temperature = Parameter.objects.create(code="Temperatura", name="Temperatura", unit="°C")
    return Variable.objects.create(point=entry, parameter=temperature, source=nalco, time_resolution=Schedule.HOURLY)


@pytest.fixture
def nalco_grid_form(nalco_form, ph_nalco, temperature_nalco):
    CaptureFormVariable.objects.create(form=nalco_form, variable=ph_nalco, order=1)
    CaptureFormVariable.objects.create(form=nalco_form, variable=temperature_nalco, order=2)
    return nalco_form


@pytest.fixture
def tablerista(nalco_grid_form):
    """An engineer with the forms: reads, captures and corrects in them (decided on 2026-10-20)."""
    user = User.objects.create_user("tablerista1", "Ana Ruiz", "x", role=User.Role.ENGINEER, must_change_password=False)
    user.capture_forms.set([nalco_grid_form])
    return user


@pytest.fixture
def capturer_with_form(capturer, nalco_grid_form):
    capturer.capture_forms.set([nalco_grid_form])
    return capturer


def save(client, form, variable, value, *, day=YESTERDAY, slot="h07", original="", **extra):
    data = {"variable": variable.pk, "slot": slot, "date": str(day), "value": value, "original": original, **extra}
    response = client.post(reverse("capture_save_cell", args=[form.pk]), data)
    return response


def answer(client, form, variable, value, **kwargs):
    response = save(client, form, variable, value, **kwargs)
    assert response.status_code == 200
    return response.json()


def measure(variable, user, when, value, precision=TimePrecision.HOUR, **fields):
    return Measurement.objects.create(
        variable=variable, taken_at=when, time_precision=precision, value=value, origin=Origin.MANUAL, created_by=user, **fields,
    )


class TestCells:
    def test_each_frequency_has_its_cells(self, ph_nalco):
        ph_nalco.time_resolution = Schedule.HOURLY
        assert [s.key for s in slots_of(ph_nalco)] == [f"h{h:02}" for h in range(24)]
        ph_nalco.time_resolution = Schedule.TWICE_DAILY
        assert [s.key for s in slots_of(ph_nalco)] == ["h07", "h16"]
        ph_nalco.time_resolution = Schedule.AM_PM
        assert [s.precision for s in slots_of(ph_nalco)] == [TimePrecision.AM, TimePrecision.PM]
        for frequency in (Schedule.DAILY, Schedule.OCCASIONAL):
            ph_nalco.time_resolution = frequency
            assert [s.precision for s in slots_of(ph_nalco)] == [TimePrecision.DAY]

    def test_hours_are_never_invented(self):
        day = datetime.date(2026, 10, 19)
        assert SLOTS["h07"].taken_at(day) == at(day, 7)
        assert SLOTS["pm"].taken_at(day) == period_start(day, TimePrecision.PM)
        assert SLOTS["d"].taken_at(day) == period_start(day, TimePrecision.DAY)

    def test_hourly_forms_have_the_hours_as_rows(self, nalco_grid_form, admin_user):
        grid = build(nalco_grid_form, YESTERDAY, admin_user)
        assert grid.slots_as_rows and len(grid.slots) == 24

    def test_other_forms_have_the_variables_as_rows(self, biota, outlet, phenols, admin_user):
        twice = Variable.objects.create(point=outlet, parameter=phenols, source=biota, time_resolution=Schedule.TWICE_DAILY)
        nitrogen = Parameter.objects.create(code="N total", name="Nitrógeno total")
        daily = Variable.objects.create(point=outlet, parameter=nitrogen, source=biota, time_resolution=Schedule.DAILY)
        form = CaptureForm.objects.create(name="BIOTA", source=biota)
        CaptureFormVariable.objects.create(form=form, variable=twice, order=1)
        CaptureFormVariable.objects.create(form=form, variable=daily, order=2)
        grid = build(form, YESTERDAY, admin_user)
        assert not grid.slots_as_rows
        assert [s.label for s in grid.slots] == ["07:00", "16:00", "Día"]
        assert not grid.cell(daily, SLOTS["h07"]).applies and grid.cell(daily, SLOTS["d"]).applies

    def test_future_hours_cannot_be_filled(self, nalco_grid_form, admin_user, ph_nalco):
        now = at(timezone.localdate(), 10)
        grid = build(nalco_grid_form, timezone.localdate(), admin_user, now=now)
        assert not grid.cell(ph_nalco, SLOTS["h10"]).readonly
        assert grid.cell(ph_nalco, SLOTS["h11"]).readonly


class TestValidation:
    def test_a_number_is_saved_with_its_history(self, admin_client, admin_user, nalco_grid_form, ph_nalco):
        result = answer(admin_client, nalco_grid_form, ph_nalco, "7,4")
        assert result["state"] == "saved" and result["value"] == "7,4"
        measurement = Measurement.objects.get()
        assert (measurement.value, measurement.origin, measurement.created_by) == (7.4, Origin.MANUAL, admin_user)
        assert measurement.taken_at == at(YESTERDAY, 7) and measurement.time_precision == TimePrecision.HOUR
        entry = MeasurementHistory.objects.get()
        assert (entry.action, entry.change, entry.user) == ("create", "— → 7,4", admin_user)

    @pytest.mark.parametrize(("text", "qualifier", "value"), [("7.4", "", 7.4), ("<0,1", "<", 0.1), ("> 9", ">", 9)])
    def test_comma_point_and_qualifiers(self, admin_client, nalco_grid_form, temperature_nalco, text, qualifier, value):
        assert answer(admin_client, nalco_grid_form, temperature_nalco, text)["state"] == "saved"
        assert (Measurement.objects.get().qualifier, Measurement.objects.get().value) == (qualifier, value)

    @pytest.mark.parametrize("text", ["7,,4", "ND", "SB", "asdfdf", "19+"])
    def test_anything_else_is_refused(self, admin_client, nalco_grid_form, ph_nalco, text):
        result = answer(admin_client, nalco_grid_form, ph_nalco, text)
        assert result["state"] == "invalid" and "Solo números" in result["message"]
        assert not Measurement.objects.exists()

    def test_outside_the_physical_range_is_refused(self, admin_client, nalco_grid_form, ph_nalco):
        result = answer(admin_client, nalco_grid_form, ph_nalco, "73")
        assert result["state"] == "invalid" and "rango físico es 0 a 14" in result["message"]
        assert not Measurement.objects.exists()

    def test_outside_the_usual_range_asks_to_confirm(self, admin_client, nalco_grid_form, ph_nalco):
        result = answer(admin_client, nalco_grid_form, ph_nalco, "4")
        assert result["state"] == "confirm" and "fuera del rango habitual (6 a 9)" in result["message"]
        assert not result["reason"] and not Measurement.objects.exists()
        assert answer(admin_client, nalco_grid_form, ph_nalco, "4", confirm="1")["state"] == "saved"

    def test_ranges_are_optional(self, admin_client, nalco_grid_form, temperature_nalco):
        assert answer(admin_client, nalco_grid_form, temperature_nalco, "4900")["state"] == "saved"

    def test_an_empty_cell_saves_nothing(self, admin_client, nalco_grid_form, ph_nalco):
        assert answer(admin_client, nalco_grid_form, ph_nalco, "  ")["state"] == "unchanged"
        assert not Measurement.objects.exists() and not MeasurementHistory.objects.exists()

    def test_future_times_are_refused(self, admin_client, nalco_grid_form, ph_nalco):
        tomorrow = timezone.localdate() + datetime.timedelta(days=1)
        assert answer(admin_client, nalco_grid_form, ph_nalco, "7", day=tomorrow)["state"] == "refused"
        assert not Measurement.objects.exists()

    def test_the_cell_must_be_one_of_the_form(self, admin_client, nalco_grid_form, ph_nalco, phenols_biota):
        assert save(admin_client, nalco_grid_form, phenols_biota, "1").status_code == 404
        assert save(admin_client, nalco_grid_form, ph_nalco, "7", slot="am").status_code == 404
        assert save(admin_client, nalco_grid_form, ph_nalco, "7", day="ayer").status_code == 404


class TestCorrections:
    def test_correcting_asks_to_confirm_and_keeps_the_reason(self, admin_client, admin_user, nalco_grid_form, ph_nalco):
        measurement = measure(ph_nalco, admin_user, at(YESTERDAY, 7), 7.3)
        result = answer(admin_client, nalco_grid_form, ph_nalco, "7,5", original=version(measurement))
        assert result["state"] == "confirm" and result["reason"] and "Corrige «7,3» por «7,5»" in result["message"]
        result = answer(admin_client, nalco_grid_form, ph_nalco, "7,5", original=version(measurement), confirm="1", reason="Mal digitado")
        assert result["state"] == "saved"
        measurement.refresh_from_db()
        assert (measurement.value, measurement.updated_by) == (7.5, admin_user)
        entry = MeasurementHistory.objects.get(action="update")
        assert (entry.change, entry.reason) == ("7,3 → 7,5", "Mal digitado")

    def test_a_corrected_suspect_value_is_no_longer_suspect(self, admin_client, admin_user, nalco_grid_form, ph_nalco):
        measurement = measure(ph_nalco, admin_user, at(YESTERDAY, 7), 73, suspect=True)
        answer(admin_client, nalco_grid_form, ph_nalco, "7,3", original=version(measurement), confirm="1")
        measurement.refresh_from_db()
        assert (measurement.value, measurement.suspect) == (7.3, False)

    def test_deleting_asks_to_confirm_and_keeps_the_history(self, admin_client, admin_user, nalco_grid_form, ph_nalco):
        measurement = measure(ph_nalco, admin_user, at(YESTERDAY, 7), 7.3)
        assert answer(admin_client, nalco_grid_form, ph_nalco, "", original=version(measurement))["state"] == "confirm"
        assert Measurement.objects.exists()
        result = answer(admin_client, nalco_grid_form, ph_nalco, "", original=version(measurement), confirm="1", reason="No se midió")
        assert result["state"] == "deleted" and not Measurement.objects.exists()
        entry = MeasurementHistory.objects.get(action="delete")
        assert (entry.change, entry.reason, entry.measurement) == ("7,3 → —", "No se midió", None)

    def test_the_same_value_changes_nothing(self, admin_client, admin_user, nalco_grid_form, ph_nalco):
        measurement = measure(ph_nalco, admin_user, at(YESTERDAY, 7), 7.3)
        assert answer(admin_client, nalco_grid_form, ph_nalco, "7.30", original=version(measurement))["state"] == "unchanged"
        assert not MeasurementHistory.objects.exists()

    def test_a_value_changed_meanwhile_is_not_overwritten(self, admin_client, admin_user, nalco_grid_form, ph_nalco):
        measurement = measure(ph_nalco, admin_user, at(YESTERDAY, 7), 7.3)
        result = answer(admin_client, nalco_grid_form, ph_nalco, "8", original="", confirm="1")
        assert result["state"] == "conflict" and result["value"] == "7,3" and result["version"] == version(measurement)
        measurement.refresh_from_db()
        assert measurement.value == 7.3


class TestWhoMayChangeWhat:
    def test_the_capturer_sees_what_is_registered(self, capturer_with_form, admin_user, ph_nalco, nalco_grid_form):
        measure(ph_nalco, admin_user, at(YESTERDAY, 7), 7.3)
        client = make_client(capturer_with_form)
        page = client.get(reverse("capture_grid", args=[nalco_grid_form.pk]), {"date": YESTERDAY.isoformat()}).content.decode()
        assert 'value="7,3"' in page
        assert "Solo puedes corregir tus propias capturas de las últimas 24 horas" in page

    def test_the_capturer_corrects_their_own_recent_captures(self, capturer_with_form, nalco_grid_form, ph_nalco):
        client = make_client(capturer_with_form)
        answer(client, nalco_grid_form, ph_nalco, "7,3")
        measurement = Measurement.objects.get()
        result = answer(client, nalco_grid_form, ph_nalco, "7,4", original=version(measurement), confirm="1")
        assert result["state"] == "saved"

    def test_but_not_those_of_others(self, capturer_with_form, admin_user, nalco_grid_form, ph_nalco):
        measurement = measure(ph_nalco, admin_user, at(YESTERDAY, 7), 7.3)
        client = make_client(capturer_with_form)
        for value in ("7,4", ""):
            result = answer(client, nalco_grid_form, ph_nalco, value, original=version(measurement), confirm="1")
            assert result["state"] == "refused"
        measurement.refresh_from_db()
        assert measurement.value == 7.3

    def test_nor_their_own_after_24_hours(self, capturer_with_form, nalco_grid_form, ph_nalco):
        measurement = measure(ph_nalco, capturer_with_form, at(YESTERDAY, 7), 7.3)
        Measurement.objects.filter(pk=measurement.pk).update(created_at=timezone.now() - datetime.timedelta(hours=25))
        measurement.refresh_from_db()
        client = make_client(capturer_with_form)
        result = answer(client, nalco_grid_form, ph_nalco, "7,4", original=version(measurement), confirm="1")
        assert result["state"] == "refused"

    def test_the_engineer_corrects_anything_in_their_forms(self, tablerista, admin_user, nalco_grid_form, ph_nalco):
        measurement = measure(ph_nalco, admin_user, at(YESTERDAY, 7), 7.3)
        result = answer(make_client(tablerista), nalco_grid_form, ph_nalco, "7,4", original=version(measurement), confirm="1")
        assert result["state"] == "saved"

    def test_forms_outside_the_scope_do_not_exist(self, capturer_with_form, biota_form, phenols_biota):
        client = make_client(capturer_with_form)
        assert client.get(reverse("capture_grid", args=[biota_form.pk])).status_code == 404
        assert save(client, biota_form, phenols_biota, "0,1").status_code == 404
        assert not Measurement.objects.exists()

    def test_an_engineer_without_forms_does_not_capture(self, engineer_client, nalco_grid_form, ph_nalco):
        assert save(engineer_client, nalco_grid_form, ph_nalco, "7").status_code == 403

    def test_the_history_of_a_cell(self, admin_client, nalco_grid_form, ph_nalco):
        answer(admin_client, nalco_grid_form, ph_nalco, "7,3")
        measurement = Measurement.objects.get()
        answer(admin_client, nalco_grid_form, ph_nalco, "7,5", original=version(measurement), confirm="1", reason="Mal digitado")
        params = {"variable": ph_nalco.pk, "slot": "h07", "date": YESTERDAY.isoformat()}
        page = admin_client.get(reverse("capture_cell_history", args=[nalco_grid_form.pk]), params).content.decode()
        assert "Mal digitado" in page and "7,3 → 7,5" in page and "— → 7,3" in page


class TestDataMigrations:
    def test_morning_and_afternoon_variables_get_their_frequency(self, admin_user, outlet, phenols, biota):
        variable = Variable.objects.create(point=outlet, parameter=phenols, source=biota, time_resolution=Schedule.TWICE_DAILY)
        Measurement.objects.create(variable=variable, taken_at=period_start(YESTERDAY, TimePrecision.AM),
                                   time_precision=TimePrecision.AM, value=1, origin=Origin.HISTORY, created_by=admin_user)
        importlib.import_module("apps.catalog.migrations.0003_am_pm_variables").mark_am_pm(django_apps, None)
        variable.refresh_from_db()
        assert variable.time_resolution == Schedule.AM_PM

    def test_initial_forms_take_the_variables_measured_since_october_2025(self, admin_user, entry, ph, nalco, nalco_form):
        recent = Variable.objects.create(point=entry, parameter=ph, source=nalco, time_resolution=Schedule.HOURLY)
        temperature = Parameter.objects.create(code="Temperatura", name="Temperatura")
        old = Variable.objects.create(point=entry, parameter=temperature, source=nalco, time_resolution=Schedule.HOURLY)
        Measurement.objects.create(variable=recent, taken_at=at(YESTERDAY, 7), time_precision="hour", value=7,
                                   origin=Origin.HISTORY, created_by=admin_user)
        Measurement.objects.create(variable=old, taken_at=at(datetime.date(2024, 1, 1), 7), time_precision="hour",
                                   value=40, origin=Origin.HISTORY, created_by=admin_user)
        migration = importlib.import_module("apps.catalog.migrations.0004_initial_capture_forms")
        migration.create_forms(django_apps, None)
        migration.create_forms(django_apps, None)
        assert list(nalco_form.variables.all()) == [recent]  # the existing «Nalco» form, completed once
        assert not CaptureForm.objects.filter(name="BIOTA Fase I").exists()  # no BIOTA variables here
        assert not Source.objects.filter(code="PI").exists() and CaptureForm.objects.count() == 1
