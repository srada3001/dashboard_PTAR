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
from apps.measurements import records
from apps.measurements.records import version
from apps.measurements.values import parse_value

from .conftest import make_client

pytestmark = pytest.mark.django_db

YESTERDAY = timezone.localdate() - datetime.timedelta(days=1)


def at(day, hour):
    return timezone.make_aware(datetime.datetime.combine(day, datetime.time(hour)))


@pytest.fixture
def entry(db):
    return SamplingPoint.objects.create(code="BA-4001", name="Entrada a la PTAR")


@pytest.fixture
def ph_ecolab(entry, ph, ecolab):
    return Variable.objects.create(point=entry, parameter=ph, source=ecolab, time_resolution=Schedule.HOURLY,
                                   typical_min=6, typical_max=9)


@pytest.fixture
def temperature_ecolab(entry, ecolab):
    temperature = Parameter.objects.create(code="Temperatura", name="Temperatura", unit="°C")
    return Variable.objects.create(point=entry, parameter=temperature, source=ecolab, time_resolution=Schedule.HOURLY)


@pytest.fixture
def ecolab_grid_form(ecolab_form, ph_ecolab, temperature_ecolab):
    CaptureFormVariable.objects.create(form=ecolab_form, variable=ph_ecolab, order=1)
    CaptureFormVariable.objects.create(form=ecolab_form, variable=temperature_ecolab, order=2)
    return ecolab_form


@pytest.fixture
def tablerista(ecolab_grid_form):
    """An engineer with the forms: reads, captures and corrects in them (decided on 2026-10-20)."""
    user = User.objects.create_user("tablerista1", "Ana Ruiz", "x", role=User.Role.ENGINEER, must_change_password=False)
    user.capture_forms.set([ecolab_grid_form])
    return user


@pytest.fixture
def capturer_with_form(capturer, ecolab_grid_form):
    capturer.capture_forms.set([ecolab_grid_form])
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
    def test_each_frequency_has_its_cells(self, ph_ecolab):
        ph_ecolab.time_resolution = Schedule.HOURLY
        assert [s.key for s in slots_of(ph_ecolab)] == [f"h{h:02}" for h in range(24)]
        ph_ecolab.time_resolution = Schedule.TWICE_DAILY
        assert [s.key for s in slots_of(ph_ecolab)] == ["h07", "h16"]
        ph_ecolab.time_resolution = Schedule.AM_PM
        assert [s.precision for s in slots_of(ph_ecolab)] == [TimePrecision.AM, TimePrecision.PM]
        for frequency in (Schedule.DAILY, Schedule.OCCASIONAL):
            ph_ecolab.time_resolution = frequency
            assert [s.precision for s in slots_of(ph_ecolab)] == [TimePrecision.DAY]

    def test_hours_are_never_invented(self):
        day = datetime.date(2026, 10, 19)
        assert SLOTS["h07"].taken_at(day) == at(day, 7)
        assert SLOTS["pm"].taken_at(day) == period_start(day, TimePrecision.PM)
        assert SLOTS["d"].taken_at(day) == period_start(day, TimePrecision.DAY)

    def test_hourly_forms_have_the_hours_as_rows(self, ecolab_grid_form, admin_user):
        grid = build(ecolab_grid_form, YESTERDAY, admin_user)
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

    def test_five_time_columns_keep_the_variables_as_rows(self, biota, outlet, phenols, admin_user):
        form = CaptureForm.objects.create(name="BIOTA", source=biota)
        for order, schedule in enumerate([Schedule.TWICE_DAILY, Schedule.AM_PM, Schedule.DAILY], start=1):
            parameter = Parameter.objects.create(code=f"P{order}", name=f"P{order}")
            variable = Variable.objects.create(point=outlet, parameter=parameter, source=biota, time_resolution=schedule)
            CaptureFormVariable.objects.create(form=form, variable=variable, order=order)
        grid = build(form, YESTERDAY, admin_user)
        assert [s.label for s in grid.slots] == ["07:00", "16:00", "a. m.", "p. m.", "Día"]
        assert not grid.slots_as_rows

    def test_sections_go_one_below_the_other_with_each_point_together(self, biota, outlet, phenols, admin_user):
        nitrogen = Parameter.objects.create(code="N total", name="Nitrógeno total")
        chamber = SamplingPoint.objects.create(code="DIAPAC cámara A")
        form = CaptureForm.objects.create(name="BIOTA", source=biota)
        variables = {}
        # The admin order mixes sections and splits the chamber, as the «DIAPAC» sheet did.
        for order, (point, parameter, section) in enumerate([
            (chamber, phenols, "DIAPAC"), (outlet, phenols, "Fase I"), (chamber, nitrogen, "DIAPAC"),
            (outlet, nitrogen, "Fase I"),
        ], start=1):
            variable = Variable.objects.create(point=point, parameter=parameter, source=biota, time_resolution=Schedule.DAILY)
            CaptureFormVariable.objects.create(form=form, variable=variable, order=order, section=section)
            variables[(point.code, parameter.code)] = variable
        rows = build(form, YESTERDAY, admin_user).variable_rows()
        assert [(v.point.code, v.parameter.code, span, section) for v, span, _, section in rows] == [
            ("DIAPAC cámara A", "Fenoles", 2, "DIAPAC"),
            ("DIAPAC cámara A", "N total", 0, ""),
            ("BA-4010", "Fenoles", 2, "Fase I"),
            ("BA-4010", "N total", 0, ""),
        ]
        page = make_client(admin_user).get(reverse("capture_grid", args=[form.pk])).content.decode()
        assert page.count('class="rejilla__seccion"') == 2
        assert form.sections() == ["DIAPAC", "Fase I"]
        assert "DIAPAC · Fase I" in make_client(admin_user).get(reverse("capture_index")).content.decode()

    def test_hours_layout_shades_every_other_point(self, ecolab_grid_form, admin_user, ph_ecolab, outlet, ph, ecolab):
        """Every other point is shaded and each one after the first starts with a thicker border; a
        stronger line every 6 hours (decided on 2026-11-11)."""
        ph_outlet = Variable.objects.create(point=outlet, parameter=ph, source=ecolab, time_resolution=Schedule.HOURLY)
        CaptureFormVariable.objects.create(form=ecolab_grid_form, variable=ph_outlet, order=3)
        grid = build(ecolab_grid_form, YESTERDAY, admin_user)
        assert [(point.code, span, css) for point, span, css in grid.point_groups()] == [
            ("BA-4001", 2, ""), ("BA-4010", 1, "rejilla__banda rejilla__inicio-col"),
        ]
        assert grid.column_classes() == ["", "", "rejilla__banda rejilla__inicio-col"]
        rows = grid.slot_rows()
        assert [slot.label for slot, _, css in rows if css] == ["06:00", "12:00", "18:00"]
        assert [css for _, css in rows[0][1]] == grid.column_classes()
        page = make_client(admin_user).get(reverse("capture_grid", args=[ecolab_grid_form.pk]), {"date": str(YESTERDAY)}).content.decode()
        assert page.count('data-jump="') == 2
        assert page.count('class="celda rejilla__banda rejilla__inicio-col') == 24

    def test_future_hours_cannot_be_filled(self, ecolab_grid_form, admin_user, ph_ecolab):
        now = at(timezone.localdate(), 10)
        grid = build(ecolab_grid_form, timezone.localdate(), admin_user, now=now)
        assert not grid.cell(ph_ecolab, SLOTS["h10"]).readonly
        assert grid.cell(ph_ecolab, SLOTS["h11"]).readonly


class TestValidation:
    def test_a_number_is_saved_with_its_history(self, admin_client, admin_user, ecolab_grid_form, ph_ecolab):
        result = answer(admin_client, ecolab_grid_form, ph_ecolab, "7,4")
        assert result["state"] == "saved" and result["value"] == "7,4"
        measurement = Measurement.objects.get()
        assert (measurement.value, measurement.origin, measurement.created_by) == (7.4, Origin.MANUAL, admin_user)
        assert measurement.taken_at == at(YESTERDAY, 7) and measurement.time_precision == TimePrecision.HOUR
        entry = MeasurementHistory.objects.get()
        assert (entry.action, entry.change, entry.user) == ("create", "— → 7,4", admin_user)

    @pytest.mark.parametrize(("text", "qualifier", "value"), [("7.4", "", 7.4), ("<0,1", "<", 0.1), ("> 9", ">", 9)])
    def test_comma_point_and_qualifiers(self, admin_client, ecolab_grid_form, temperature_ecolab, text, qualifier, value):
        assert answer(admin_client, ecolab_grid_form, temperature_ecolab, text)["state"] == "saved"
        assert (Measurement.objects.get().qualifier, Measurement.objects.get().value) == (qualifier, value)

    @pytest.mark.parametrize("text", ["7,,4", "ND", "SB", "asdfdf", "19+"])
    def test_anything_else_is_refused(self, admin_client, ecolab_grid_form, ph_ecolab, text):
        result = answer(admin_client, ecolab_grid_form, ph_ecolab, text)
        assert result["state"] == "invalid" and "Solo números" in result["message"]
        assert not Measurement.objects.exists()

    def test_outside_the_physical_range_is_refused(self, admin_client, ecolab_grid_form, ph_ecolab):
        result = answer(admin_client, ecolab_grid_form, ph_ecolab, "73")
        assert result["state"] == "invalid" and "rango físico es 0 a 14" in result["message"]
        assert not Measurement.objects.exists()

    def test_outside_the_usual_range_asks_to_confirm(self, admin_client, ecolab_grid_form, ph_ecolab):
        result = answer(admin_client, ecolab_grid_form, ph_ecolab, "4")
        assert result["state"] == "confirm" and "fuera del rango habitual (6 a 9)" in result["message"]
        assert not result["reason"] and not Measurement.objects.exists()
        assert answer(admin_client, ecolab_grid_form, ph_ecolab, "4", confirm="1")["state"] == "saved"

    def test_ranges_are_optional(self, admin_client, ecolab_grid_form, temperature_ecolab):
        assert answer(admin_client, ecolab_grid_form, temperature_ecolab, "4900")["state"] == "saved"

    def test_an_empty_cell_saves_nothing(self, admin_client, ecolab_grid_form, ph_ecolab):
        assert answer(admin_client, ecolab_grid_form, ph_ecolab, "  ")["state"] == "unchanged"
        assert not Measurement.objects.exists() and not MeasurementHistory.objects.exists()

    def test_future_times_are_refused(self, admin_client, ecolab_grid_form, ph_ecolab):
        tomorrow = timezone.localdate() + datetime.timedelta(days=1)
        assert answer(admin_client, ecolab_grid_form, ph_ecolab, "7", day=tomorrow)["state"] == "refused"
        assert not Measurement.objects.exists()

    def test_the_cell_must_be_one_of_the_form(self, admin_client, ecolab_grid_form, ph_ecolab, phenols_biota):
        assert save(admin_client, ecolab_grid_form, phenols_biota, "1").status_code == 404
        assert save(admin_client, ecolab_grid_form, ph_ecolab, "7", slot="am").status_code == 404
        assert save(admin_client, ecolab_grid_form, ph_ecolab, "7", day="ayer").status_code == 404


class TestCorrections:
    def test_correcting_asks_to_confirm_and_keeps_the_reason(self, admin_client, admin_user, ecolab_grid_form, ph_ecolab):
        measurement = measure(ph_ecolab, admin_user, at(YESTERDAY, 7), 7.3)
        result = answer(admin_client, ecolab_grid_form, ph_ecolab, "7,5", original=version(measurement))
        assert result["state"] == "confirm" and result["reason"] and "Corrige «7,3» por «7,5»" in result["message"]
        result = answer(admin_client, ecolab_grid_form, ph_ecolab, "7,5", original=version(measurement), confirm="1", reason="Mal digitado")
        assert result["state"] == "saved"
        measurement.refresh_from_db()
        assert (measurement.value, measurement.updated_by) == (7.5, admin_user)
        entry = MeasurementHistory.objects.get(action="update")
        assert (entry.change, entry.reason) == ("7,3 → 7,5", "Mal digitado")

    def test_a_corrected_suspect_value_is_no_longer_suspect(self, admin_client, admin_user, ecolab_grid_form, ph_ecolab):
        measurement = measure(ph_ecolab, admin_user, at(YESTERDAY, 7), 73, suspect=True)
        answer(admin_client, ecolab_grid_form, ph_ecolab, "7,3", original=version(measurement), confirm="1")
        measurement.refresh_from_db()
        assert (measurement.value, measurement.suspect) == (7.3, False)

    def test_deleting_asks_to_confirm_and_keeps_the_history(self, admin_client, admin_user, ecolab_grid_form, ph_ecolab):
        measurement = measure(ph_ecolab, admin_user, at(YESTERDAY, 7), 7.3)
        assert answer(admin_client, ecolab_grid_form, ph_ecolab, "", original=version(measurement))["state"] == "confirm"
        assert Measurement.objects.exists()
        result = answer(admin_client, ecolab_grid_form, ph_ecolab, "", original=version(measurement), confirm="1", reason="No se midió")
        assert result["state"] == "deleted" and not Measurement.objects.exists()
        entry = MeasurementHistory.objects.get(action="delete")
        assert (entry.change, entry.reason, entry.measurement) == ("7,3 → —", "No se midió", None)

    def test_the_same_value_changes_nothing(self, admin_client, admin_user, ecolab_grid_form, ph_ecolab):
        measurement = measure(ph_ecolab, admin_user, at(YESTERDAY, 7), 7.3)
        assert answer(admin_client, ecolab_grid_form, ph_ecolab, "7.30", original=version(measurement))["state"] == "unchanged"
        assert not MeasurementHistory.objects.exists()

    def test_a_value_changed_meanwhile_is_not_overwritten(self, admin_client, admin_user, ecolab_grid_form, ph_ecolab):
        measurement = measure(ph_ecolab, admin_user, at(YESTERDAY, 7), 7.3)
        result = answer(admin_client, ecolab_grid_form, ph_ecolab, "8", original="", confirm="1")
        assert result["state"] == "conflict" and result["value"] == "7,3" and result["version"] == version(measurement)
        measurement.refresh_from_db()
        assert measurement.value == 7.3


class TestWhoMayChangeWhat:
    def test_the_capturer_sees_what_is_registered(self, capturer_with_form, admin_user, ph_ecolab, ecolab_grid_form):
        measure(ph_ecolab, admin_user, at(YESTERDAY, 7), 7.3)
        client = make_client(capturer_with_form)
        page = client.get(reverse("capture_grid", args=[ecolab_grid_form.pk]), {"date": YESTERDAY.isoformat()}).content.decode()
        assert 'value="7,3"' in page
        assert "Solo puedes corregir tus propias capturas de las últimas 48 horas" in page

    def test_the_capturer_corrects_their_own_recent_captures(self, capturer_with_form, ecolab_grid_form, ph_ecolab):
        client = make_client(capturer_with_form)
        answer(client, ecolab_grid_form, ph_ecolab, "7,3")
        measurement = Measurement.objects.get()
        result = answer(client, ecolab_grid_form, ph_ecolab, "7,4", original=version(measurement), confirm="1")
        assert result["state"] == "saved"

    def test_but_not_those_of_others(self, capturer_with_form, admin_user, ecolab_grid_form, ph_ecolab):
        measurement = measure(ph_ecolab, admin_user, at(YESTERDAY, 7), 7.3)
        client = make_client(capturer_with_form)
        for value in ("7,4", ""):
            result = answer(client, ecolab_grid_form, ph_ecolab, value, original=version(measurement), confirm="1")
            assert result["state"] == "refused"
        measurement.refresh_from_db()
        assert measurement.value == 7.3

    def test_their_own_for_48_hours_and_not_after(self, capturer_with_form, ecolab_grid_form, ph_ecolab):
        measurement = measure(ph_ecolab, capturer_with_form, at(YESTERDAY, 7), 7.3)
        client = make_client(capturer_with_form)
        Measurement.objects.filter(pk=measurement.pk).update(created_at=timezone.now() - datetime.timedelta(hours=30))
        measurement.refresh_from_db()
        result = answer(client, ecolab_grid_form, ph_ecolab, "7,4", original=version(measurement), confirm="1")
        assert result["state"] == "saved"  # 30 hours: before 2026-11-09 it was refused (24)
        measurement.refresh_from_db()
        Measurement.objects.filter(pk=measurement.pk).update(created_at=timezone.now() - datetime.timedelta(hours=49))
        measurement.refresh_from_db()
        result = answer(client, ecolab_grid_form, ph_ecolab, "7,5", original=version(measurement), confirm="1")
        assert result["state"] == "refused"

    def test_the_capturer_fills_only_the_last_48_hours(self, capturer_with_form, ecolab_grid_form, ph_ecolab):
        client = make_client(capturer_with_form)
        old_day = timezone.localdate() - datetime.timedelta(days=3)
        result = answer(client, ecolab_grid_form, ph_ecolab, "7,3", day=old_day)
        assert result == {"state": "refused", "message": "Solo puedes llenar datos de las últimas 48 horas."}
        assert not Measurement.objects.exists()
        page = client.get(reverse("capture_grid", args=[ecolab_grid_form.pk]), {"date": old_day.isoformat()}).content.decode()
        assert "Solo puedes llenar datos de las últimas 48 horas" in page  # the cell is read-only, with the reason
        assert answer(client, ecolab_grid_form, ph_ecolab, "7,3")["state"] == "saved"  # yesterday, 07:00

    def test_the_engineer_fills_only_the_last_48_hours_too(self, tablerista, ecolab_grid_form, ph_ecolab):
        client = make_client(tablerista)
        old_day = timezone.localdate() - datetime.timedelta(days=3)
        result = answer(client, ecolab_grid_form, ph_ecolab, "7,3", day=old_day)
        assert result == {"state": "refused", "message": "Solo puedes llenar datos de las últimas 48 horas."}
        assert answer(client, ecolab_grid_form, ph_ecolab, "7,3")["state"] == "saved"  # yesterday, 07:00

    def test_the_engineer_corrects_anything_in_their_forms_of_the_last_48_hours(self, tablerista, admin_user, ecolab_grid_form, ph_ecolab):
        measurement = measure(ph_ecolab, admin_user, at(YESTERDAY, 7), 7.3)  # someone else's, just registered
        client = make_client(tablerista)
        result = answer(client, ecolab_grid_form, ph_ecolab, "7,4", original=version(measurement), confirm="1")
        assert result["state"] == "saved"
        Measurement.objects.filter(pk=measurement.pk).update(created_at=timezone.now() - datetime.timedelta(hours=49))
        measurement.refresh_from_db()
        result = answer(client, ecolab_grid_form, ph_ecolab, "7,5", original=version(measurement), confirm="1")
        assert result == {"state": "refused", "message": "Solo puedes corregir capturas de las últimas 48 horas; más atrás, el administrador."}

    def test_only_the_administrator_has_no_time_limit(self, admin_client, admin_user, ecolab_grid_form, ph_ecolab):
        old_day = timezone.localdate() - datetime.timedelta(days=30)
        assert answer(admin_client, ecolab_grid_form, ph_ecolab, "7,3", day=old_day)["state"] == "saved"
        measurement = Measurement.objects.get()
        Measurement.objects.filter(pk=measurement.pk).update(created_at=timezone.now() - datetime.timedelta(days=30))
        measurement.refresh_from_db()
        result = answer(admin_client, ecolab_grid_form, ph_ecolab, "7,4", day=old_day, original=version(measurement), confirm="1")
        assert result["state"] == "saved"

    def test_forms_outside_the_scope_do_not_exist(self, capturer_with_form, biota_form, phenols_biota):
        client = make_client(capturer_with_form)
        assert client.get(reverse("capture_grid", args=[biota_form.pk])).status_code == 404
        assert save(client, biota_form, phenols_biota, "0,1").status_code == 404
        assert not Measurement.objects.exists()

    def test_an_engineer_without_forms_does_not_capture(self, engineer_client, ecolab_grid_form, ph_ecolab):
        assert save(engineer_client, ecolab_grid_form, ph_ecolab, "7").status_code == 403

    def test_the_history_of_a_cell(self, admin_client, ecolab_grid_form, ph_ecolab):
        answer(admin_client, ecolab_grid_form, ph_ecolab, "7,3")
        measurement = Measurement.objects.get()
        answer(admin_client, ecolab_grid_form, ph_ecolab, "7,5", original=version(measurement), confirm="1", reason="Mal digitado")
        params = {"variable": ph_ecolab.pk, "slot": "h07", "date": YESTERDAY.isoformat()}
        page = admin_client.get(reverse("capture_cell_history", args=[ecolab_grid_form.pk]), params).content.decode()
        assert "Mal digitado" in page and "7,3 → 7,5" in page and "— → 7,3" in page


class TestDataMigrations:
    def test_morning_and_afternoon_variables_get_their_frequency(self, admin_user, outlet, phenols, biota):
        variable = Variable.objects.create(point=outlet, parameter=phenols, source=biota, time_resolution=Schedule.TWICE_DAILY)
        Measurement.objects.create(variable=variable, taken_at=period_start(YESTERDAY, TimePrecision.AM),
                                   time_precision=TimePrecision.AM, value=1, origin=Origin.HISTORY, created_by=admin_user)
        importlib.import_module("apps.catalog.migrations.0003_am_pm_variables").mark_am_pm(django_apps, None)
        variable.refresh_from_db()
        assert variable.time_resolution == Schedule.AM_PM

    def test_initial_forms_take_the_variables_measured_since_october_2025(self, admin_user, entry, ph, ecolab, ecolab_form):
        # When this migration ran, Ecolab was still called Nalco (catalog/0014 renamed it).
        ecolab.code, ecolab_form.name = "Nalco", "Nalco"
        ecolab.save()
        ecolab_form.save()
        recent = Variable.objects.create(point=entry, parameter=ph, source=ecolab, time_resolution=Schedule.HOURLY)
        temperature = Parameter.objects.create(code="Temperatura", name="Temperatura")
        old = Variable.objects.create(point=entry, parameter=temperature, source=ecolab, time_resolution=Schedule.HOURLY)
        Measurement.objects.create(variable=recent, taken_at=at(YESTERDAY, 7), time_precision="hour", value=7,
                                   origin=Origin.HISTORY, created_by=admin_user)
        Measurement.objects.create(variable=old, taken_at=at(datetime.date(2024, 1, 1), 7), time_precision="hour",
                                   value=40, origin=Origin.HISTORY, created_by=admin_user)
        migration = importlib.import_module("apps.catalog.migrations.0004_initial_capture_forms")
        migration.create_forms(django_apps, None)
        migration.create_forms(django_apps, None)
        assert list(ecolab_form.variables.all()) == [recent]  # the existing «Nalco» form, completed once
        assert not CaptureForm.objects.filter(name="BIOTA Fase I").exists()  # no BIOTA variables here
        assert not Source.objects.filter(code="PI").exists() and CaptureForm.objects.count() == 1

    def test_diapac_moves_to_the_biota_form(self, admin_user, capturer, biota, outlet, phenols, biota_form):
        pending = Source.objects.create(code="Por confirmar", name="Por confirmar")
        labviewer = Source.objects.create(code="Labviewer", name="Laboratorio central")
        afluente, chamber_a = (SamplingPoint.objects.create(code=code) for code in ("DIAPAC afluente", "DIAPAC cámara A"))
        effluent = SamplingPoint.objects.create(code="DIAPAC efluente")
        nitrogen = Parameter.objects.create(code="N total", name="Nitrógeno total")
        lab_effluent = Variable.objects.create(point=effluent, parameter=phenols, source=labviewer)
        diapac = CaptureForm.objects.create(name="DIAPAC", source=pending, schedule=Schedule.OCCASIONAL)
        keys = [(afluente, phenols), (chamber_a, phenols), (afluente, nitrogen), (chamber_a, nitrogen)]
        moved = []
        for order, (point, parameter) in enumerate(keys, start=1):
            variable = Variable.objects.create(point=point, parameter=parameter, source=pending, time_resolution=Schedule.OCCASIONAL)
            Measurement.objects.create(variable=variable, taken_at=period_start(YESTERDAY, TimePrecision.DAY),
                                       time_precision=TimePrecision.DAY, value=order, origin=Origin.HISTORY, created_by=admin_user)
            CaptureFormVariable.objects.create(form=diapac, variable=variable, order=order)
            moved.append(variable)
        capturer.capture_forms.add(diapac)

        migration = importlib.import_module("apps.catalog.migrations.0007_diapac_to_biota")
        migration.move_diapac(django_apps, None)
        migration.move_diapac(django_apps, None)

        assert set(Variable.objects.filter(pk__in=[v.pk for v in moved]).values_list("source__code", flat=True)) == {"BIOTA"}
        assert Measurement.objects.filter(variable__source=biota).count() == 4  # the measurements go with them
        lab_effluent.refresh_from_db()
        assert lab_effluent.source == labviewer  # the effluent is Labviewer's
        assert not CaptureForm.objects.filter(name="DIAPAC").exists()
        form = CaptureForm.objects.get()
        assert form.pk == biota_form.pk and form.name == "BIOTA"
        items = [(item.section, str(item.variable.point), str(item.variable.parameter)) for item in form.items.select_related("variable__point", "variable__parameter")]
        assert items == [
            ("Fase I", "BA-4010", "Fenoles"),
            ("DIAPAC", "DIAPAC afluente", "Fenoles"),
            ("DIAPAC", "DIAPAC afluente", "N total"),
            ("DIAPAC", "DIAPAC cámara A", "Fenoles"),
            ("DIAPAC", "DIAPAC cámara A", "N total"),
        ]
        assert list(capturer.capture_forms.all()) == [form]  # whoever had «DIAPAC» now has «BIOTA»

    def test_without_the_forms_only_the_variables_move(self, biota):
        migration = importlib.import_module("apps.catalog.migrations.0007_diapac_to_biota")
        migration.move_diapac(django_apps, None)
        assert not CaptureForm.objects.exists()

    def test_ecodiesel_moves_to_the_biota_form_below_diapac(self, admin_user, capturer, biota, phenols, biota_form):
        pending = Source.objects.create(code="Por confirmar", name="Por confirmar")
        biota_form.name = "BIOTA"
        biota_form.save()
        point = SamplingPoint.objects.create(code="Ecodiesel")
        variable = Variable.objects.create(point=point, parameter=phenols, source=pending, time_resolution=Schedule.OCCASIONAL)
        Measurement.objects.create(variable=variable, taken_at=period_start(YESTERDAY, TimePrecision.DAY),
                                   time_precision=TimePrecision.DAY, value=3, origin=Origin.HISTORY, created_by=admin_user)
        ecodiesel = CaptureForm.objects.create(name="Ecodiesel", source=pending, schedule=Schedule.OCCASIONAL)
        CaptureFormVariable.objects.create(form=ecodiesel, variable=variable, order=1)
        capturer.capture_forms.add(ecodiesel)

        migration = importlib.import_module("apps.catalog.migrations.0008_ecodiesel_to_biota")
        migration.move_ecodiesel(django_apps, None)
        migration.move_ecodiesel(django_apps, None)

        variable.refresh_from_db()
        assert variable.source == biota and variable.measurements.count() == 1
        assert list(CaptureForm.objects.all()) == [biota_form]
        last = biota_form.items.last()
        assert (last.variable, last.section) == (variable, "Ecodiesel")
        assert list(capturer.capture_forms.all()) == [biota_form]

    def test_the_clarifiers_are_ba_4005_and_their_flows_go_in_one_hourly_form(self, admin_user, capturer, ecolab, ph):
        pi = Source.objects.create(code="PI", name="PI")
        pending = Source.objects.create(code="Por confirmar", name="Por confirmar")
        flow = Parameter.objects.create(code="Flujo", name="Flujo", unit="gpm")
        ba_c = SamplingPoint.objects.create(code="BA-4005C")
        ecolab_ph = Variable.objects.create(point=ba_c, parameter=ph, source=ecolab)
        pi_c = Variable.objects.create(point=ba_c, parameter=flow, source=pi, time_resolution=Schedule.HOURLY)
        clarifier_a, clarifier_c = (SamplingPoint.objects.create(code=f"Clarificador {x}") for x in "AC")
        recirculation = SamplingPoint.objects.create(code="Recirculación")
        daily_a, daily_c = (Variable.objects.create(point=p, parameter=flow, source=pending) for p in (clarifier_a, clarifier_c))
        Measurement.objects.create(variable=daily_c, taken_at=period_start(YESTERDAY, TimePrecision.DAY),
                                   time_precision=TimePrecision.DAY, value=1800, origin=Origin.HISTORY, created_by=admin_user)
        pi_form = CaptureForm.objects.create(name="Flujos de PI", source=pi, schedule=Schedule.HOURLY)
        CaptureFormVariable.objects.create(form=pi_form, variable=pi_c, order=1)
        daily_form = CaptureForm.objects.create(name="Flujos y niveles del laboratorio", source=pending)
        CaptureFormVariable.objects.create(form=daily_form, variable=daily_a, order=1)
        capturer.capture_forms.add(daily_form)

        migration = importlib.import_module("apps.catalog.migrations.0009_load_flows")
        migration.apply(django_apps, None)
        migration.apply(django_apps, None)

        clarifier_a.refresh_from_db()
        assert (clarifier_a.code, clarifier_a.name) == ("BA-4005A", "Clarificador A")  # renamed: no BA-4005A before
        assert not SamplingPoint.objects.filter(code="Clarificador C").exists()  # merged into BA-4005C
        daily_c.refresh_from_db()
        assert daily_c.point == ba_c and daily_c.measurements.count() == 1 and daily_c.source == pending
        assert set(ba_c.variables.all()) == {ecolab_ph, pi_c, daily_c}
        assert set(ba_c.aliases.values_list("alias", flat=True)) == {"Clarificador C"}
        assert not CaptureForm.objects.filter(name__in=["Flujos de PI", "Flujos y niveles del laboratorio"]).exists()
        form = CaptureForm.objects.get(name="Flujos de carga")
        assert form.pk == pi_form.pk and form.schedule == Schedule.HOURLY
        assert [str(item.variable) for item in form.items.all()] == [
            "BA-4005A · Flujo · PI", "BA-4005C · Flujo · PI", "Recirculación · Flujo · PI",
        ]
        assert {v.time_resolution for v in form.variables.all()} == {Schedule.HOURLY}
        assert list(capturer.capture_forms.all()) == [form]

    def test_only_the_most_complete_flow_stays_in_the_history(self, admin_user):
        pi = Source.objects.create(code="PI", name="PI")
        pending = Source.objects.create(code="Por confirmar", name="Por confirmar")
        flow = Parameter.objects.create(code="Flujo", name="Flujo", unit="gpm")
        ba_c, ba_a = (SamplingPoint.objects.create(code=code) for code in ("BA-4005C", "BA-4005A"))
        hourly = Variable.objects.create(point=ba_c, parameter=flow, source=pi, time_resolution=Schedule.HOURLY)
        daily = Variable.objects.create(point=ba_c, parameter=flow, source=pending)
        only_daily = Variable.objects.create(point=ba_a, parameter=flow, source=pending)
        Variable.objects.create(point=ba_a, parameter=flow, source=pi, time_resolution=Schedule.HOURLY)  # still empty
        for hour in (6, 7):
            Measurement.objects.create(variable=hourly, taken_at=at(YESTERDAY, hour), time_precision=TimePrecision.HOUR,
                                       value=1800 + hour, origin=Origin.HISTORY, created_by=admin_user)
        for variable in (daily, only_daily):  # with their history, as the import leaves them
            records.write(variable, period_start(YESTERDAY, TimePrecision.DAY), TimePrecision.DAY, parse_value("1803"), admin_user)

        migration = importlib.import_module("apps.catalog.migrations.0010_one_flow_per_clarifier")
        migration.keep_most_complete(django_apps, None)
        migration.keep_most_complete(django_apps, None)

        assert hourly.measurements.count() == 2
        # While the platform is being built, the repeated flow goes completely, history included.
        assert not Variable.objects.filter(pk=daily.pk).exists()
        assert not MeasurementHistory.objects.filter(variable_id=daily.pk).exists()
        assert only_daily.measurements.count() == 1  # the only flow with data at BA-4005A stays

    def test_separators_and_caustic_move_to_the_biota_form(self, admin_user, capturer, biota, phenols, biota_form):
        pending = Source.objects.create(code="Por confirmar", name="Por confirmar")
        biota_form.name = "BIOTA"
        biota_form.save()
        forms = {}
        for name, code, schedule in [("Separadores y agua agria", "SE-3010", Schedule.AM_PM),
                                     ("Sodas gastadas", "K-4090", Schedule.OCCASIONAL)]:
            variable = Variable.objects.create(point=SamplingPoint.objects.create(code=code), parameter=phenols,
                                               source=pending, time_resolution=schedule)
            forms[name] = CaptureForm.objects.create(name=name, source=pending, schedule=schedule)
            CaptureFormVariable.objects.create(form=forms[name], variable=variable, order=1)
        not_moved = Variable.objects.create(point=SamplingPoint.objects.create(code="Piscina pulmón"), parameter=phenols, source=pending)
        capturer.capture_forms.add(forms["Sodas gastadas"])

        migration = importlib.import_module("apps.catalog.migrations.0011_separators_and_caustic_to_biota")
        migration.move_to_biota(django_apps, None)
        migration.move_to_biota(django_apps, None)

        assert list(CaptureForm.objects.all()) == [biota_form]
        items = [(item.section, str(item.variable)) for item in biota_form.items.select_related("variable__point", "variable__parameter", "variable__source")]
        assert items[1:] == [
            ("Aguas agrias a los separadores", "SE-3010 · Fenoles · BIOTA"),
            ("Sodas gastadas", "K-4090 · Fenoles · BIOTA"),
        ]
        not_moved.refresh_from_db()
        assert not_moved.source == pending  # the levels of «Datos LABORATORIO» stay «Por confirmar»
        assert list(capturer.capture_forms.all()) == [biota_form]

    def test_biota_values_go_to_7_am_and_4_pm(self, admin_user, biota, outlet, phenols):
        nitrogen = Parameter.objects.create(code="N total", name="Nitrógeno total")
        daily = Variable.objects.create(point=outlet, parameter=nitrogen, source=biota, time_resolution=Schedule.DAILY)
        separators = Variable.objects.create(point=SamplingPoint.objects.create(code="SE-3010"), parameter=phenols,
                                             source=biota, time_resolution=Schedule.AM_PM)
        still_afternoon = Variable.objects.create(point=SamplingPoint.objects.create(code="BR-4081"), parameter=phenols,
                                                  source=biota, time_resolution=Schedule.TWICE_DAILY)
        labviewer = Source.objects.create(code="Labviewer", name="Laboratorio central")
        lab = Variable.objects.create(point=outlet, parameter=nitrogen, source=labviewer, time_resolution=Schedule.DAILY)
        day = datetime.date(2026, 7, 4)  # the last afternoon of most of BIOTA
        for variable, precision in [(daily, TimePrecision.DAY), (separators, TimePrecision.AM),
                                    (separators, TimePrecision.PM), (lab, TimePrecision.DAY)]:
            records.write(variable, period_start(day, precision), precision, parse_value("5"), admin_user)
        records.write(still_afternoon, at(datetime.date(2026, 10, 12), 16), TimePrecision.HOUR, parse_value("2"), admin_user)

        migration = importlib.import_module("apps.catalog.migrations.0013_biota_morning_samples")
        migration.to_morning(django_apps, None)
        migration.to_morning(django_apps, None)

        moved = Measurement.objects.get(variable=daily)
        assert (moved.taken_at, moved.time_precision) == (at(day, 7), TimePrecision.HOUR)
        assert sorted(Measurement.objects.filter(variable=separators).values_list("taken_at", flat=True)) == [at(day, 7), at(day, 16)]
        # The history moves with each value, so the cell at 7 a.m. shows it.
        assert MeasurementHistory.objects.get(variable=daily).taken_at == at(day, 7)
        assert Measurement.objects.get(variable=lab).time_precision == TimePrecision.DAY  # only BIOTA
        frequencies = {v.pk: v.time_resolution for v in Variable.objects.all()}
        assert frequencies[daily.pk] == frequencies[separators.pk] == Schedule.MORNING
        assert frequencies[still_afternoon.pk] == Schedule.TWICE_DAILY  # 4 p.m. values since September 2026
        assert frequencies[lab.pk] == Schedule.DAILY

        form = CaptureForm.objects.create(name="BIOTA", source=biota)
        for order, variable in enumerate([daily, still_afternoon], start=1):
            CaptureFormVariable.objects.create(form=form, variable=Variable.objects.get(pk=variable.pk), order=order)
        grid = build(form, day, admin_user)
        assert [s.label for s in grid.slots] == ["07:00", "16:00"]
        assert grid.cell(Variable.objects.get(pk=daily.pk), SLOTS["h07"]).value == "5"
        assert not grid.cell(Variable.objects.get(pk=daily.pk), SLOTS["h16"]).applies

    def test_nalco_is_now_ecolab(self, ecolab):
        ecolab.code = "Nalco"
        ecolab.save()
        form = CaptureForm.objects.create(name="Nalco", source=ecolab)
        migration = importlib.import_module("apps.catalog.migrations.0014_nalco_is_ecolab")
        migration.rename(django_apps, None)
        migration.rename(django_apps, None)
        ecolab.refresh_from_db()
        form.refresh_from_db()
        assert (ecolab.code, form.name) == ("Ecolab", "Ecolab")
