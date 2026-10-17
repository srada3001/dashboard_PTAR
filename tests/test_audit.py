"""Changes to users, catalogs, ranges and limits leave an AuditEntry with before and after."""

import pytest
from django.urls import reverse

from apps.catalog.models import Parameter
from apps.core.models import AuditEntry

pytestmark = pytest.mark.django_db


def parameter_data(**overrides):
    data = {"code": "Fenoles", "name": "Fenoles", "unit": "mg/L", "decimals": 2, "is_active": "on"}
    data.update(overrides)
    return data


class TestCatalogAudit:
    def test_creation_records_the_values(self, admin_client, admin_user):
        response = admin_client.post(reverse("admin:catalog_parameter_add"), parameter_data())
        assert response.status_code == 302
        entry = AuditEntry.objects.get()
        assert entry.action == AuditEntry.Action.CREATE
        assert entry.actor == admin_user
        assert entry.object_repr == "Fenoles"
        assert entry.changes["Unidad"] == ["", "mg/L"]

    def test_change_records_before_and_after(self, admin_client, phenols):
        url = reverse("admin:catalog_parameter_change", args=[phenols.pk])
        admin_client.post(url, parameter_data(unit="ppm", physical_min="0"))
        entry = AuditEntry.objects.get()
        assert entry.action == AuditEntry.Action.UPDATE
        assert entry.changes == {"Unidad": ["mg/L", "ppm"], "Mínimo físico": ["", "0.0"]}

    def test_saving_without_changes_records_nothing(self, admin_client, phenols):
        admin_client.post(reverse("admin:catalog_parameter_change", args=[phenols.pk]), parameter_data())
        assert not AuditEntry.objects.exists()

    def test_deletion_is_recorded(self, admin_client, phenols):
        admin_client.post(reverse("admin:catalog_parameter_delete", args=[phenols.pk]), {"post": "yes"})
        assert not Parameter.objects.exists()
        entry = AuditEntry.objects.get()
        assert entry.action == AuditEntry.Action.DELETE
        assert entry.object_repr == "Fenoles"

    def test_inline_rows_are_recorded(self, admin_client, outlet):
        url = reverse("admin:catalog_samplingpoint_change", args=[outlet.pk])
        admin_client.post(
            url,
            {
                "code": "BA-4010",
                "name": outlet.name,
                "area": outlet.area_id,
                "order": 0,
                "is_active": "on",
                "aliases-TOTAL_FORMS": "1",
                "aliases-INITIAL_FORMS": "0",
                "aliases-0-alias": "VERTEDERO BA4010",
            },
        )
        entry = AuditEntry.objects.get()
        assert entry.changes == {"Alias «VERTEDERO BA4010»": ["", "agregado"]}


class TestUserAudit:
    def test_capture_forms_and_role_changes_are_recorded(self, admin_client, capturer, biota_form):
        url = reverse("admin:accounts_user_change", args=[capturer.pk])
        admin_client.post(
            url,
            {
                "username": capturer.username,
                "full_name": capturer.full_name,
                "role": "engineer",
                "capture_forms": [biota_form.pk],
                "is_active": "on",
            },
        )
        entry = AuditEntry.objects.get()
        assert entry.changes == {"Rol": ["Capturista", "Ingeniero"], "Formatos de captura": ["", "BIOTA Fase I"]}

    def test_passwords_never_reach_the_log(self, admin_client):
        admin_client.post(
            reverse("admin:accounts_user_add"),
            {
                "username": "nuevo",
                "full_name": "Persona Nueva",
                "role": "capturer",
                "password1": "Temporal-segura-123",
                "password2": "Temporal-segura-123",
            },
        )
        entry = AuditEntry.objects.get()
        assert "Temporal-segura-123" not in str(entry.changes)
        assert entry.changes["Usuario"] == ["", "nuevo"]

    def test_temporary_password_is_recorded_without_the_password(self, admin_client, engineer):
        url = reverse("admin:auth_user_password_change", args=[engineer.pk])
        admin_client.post(
            url, {"password1": "Temporal-segura-123", "password2": "Temporal-segura-123", "usable_password": "true"}
        )
        entry = AuditEntry.objects.get()
        assert entry.changes == {"Contraseña": ["", "temporal asignada"]}


class TestAdminPages:
    MODELS = ["source", "processarea", "samplingpoint", "parameter", "variable", "limit", "captureform"]

    @pytest.mark.parametrize("model", MODELS)
    def test_catalog_lists_and_forms_open(self, admin_client, biota_form, model):
        assert admin_client.get(reverse(f"admin:catalog_{model}_changelist")).status_code == 200
        assert admin_client.get(reverse(f"admin:catalog_{model}_add")).status_code == 200

    def test_user_pages_open(self, admin_client, capturer):
        assert admin_client.get(reverse("admin:accounts_user_changelist")).status_code == 200
        assert admin_client.get(reverse("admin:accounts_user_add")).status_code == 200
        assert admin_client.get(reverse("admin:accounts_user_change", args=[capturer.pk])).status_code == 200

    def test_django_groups_are_hidden(self, admin_client):
        # Permissions come from the role; groups would only confuse.
        assert "Grupos" not in admin_client.get(reverse("admin:index")).content.decode()


class TestAuditLogIsReadOnly:
    def test_nobody_edits_or_deletes_entries(self, admin_client, admin_user, phenols):
        entry = AuditEntry.record(admin_user, AuditEntry.Action.UPDATE, phenols, {"Unidad": ["a", "b"]})
        assert admin_client.get(reverse("admin:core_auditentry_add")).status_code == 403
        assert admin_client.get(reverse("admin:core_auditentry_delete", args=[entry.pk])).status_code == 403
