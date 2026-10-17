from datetime import timedelta
from io import StringIO

import pytest
from axes.models import AccessAttempt
from django.core.management import CommandError, call_command
from django.urls import reverse
from django.utils import timezone

from apps.accounts.lockout import is_locked
from apps.accounts.models import User

from .conftest import PASSWORD

pytestmark = pytest.mark.django_db


def login(client, username, password):
    return client.post(reverse("login"), {"username": username, "password": password})


def fail_login(client, username, times):
    for _ in range(times):
        login(client, username, "wrong-password")


class TestLogin:
    def test_valid_credentials_go_to_home(self, client, engineer):
        response = login(client, "ingeniero", PASSWORD)
        assert response.status_code == 302
        assert response.url == reverse("home")

    def test_anonymous_is_sent_to_login(self, client):
        response = client.get(reverse("home"))
        assert response.status_code == 302
        assert response.url.startswith(reverse("login"))

    def test_create_superuser_is_admin_without_forced_change(self, admin_user):
        assert admin_user.is_admin and admin_user.is_staff and admin_user.is_superuser
        assert not admin_user.must_change_password

    def test_new_people_are_capturers_who_must_change_password(self):
        user = User.objects.create_user("nuevo", "Persona Nueva", PASSWORD)
        assert user.role == User.Role.CAPTURER
        assert user.must_change_password
        assert not user.can_read

    def test_session_cookie_is_named_for_firebase(self, client, engineer):
        # Firebase Hosting only forwards the "__session" cookie to Cloud Run.
        login(client, "ingeniero", PASSWORD)
        assert "__session" in client.cookies
        assert "csrftoken" not in client.cookies  # the CSRF token lives in the session

    def test_usernames_are_unique_ignoring_case(self, engineer):
        from django.core.exceptions import ValidationError

        duplicate = User(username="INGENIERO", full_name="Otra persona")
        duplicate.set_password(PASSWORD)
        with pytest.raises(ValidationError, match="Ya existe una persona con ese usuario"):
            duplicate.full_clean()


class TestLockout:
    def test_nine_failures_do_not_lock(self, client, engineer):
        fail_login(client, "ingeniero", 9)
        assert not is_locked("ingeniero")
        assert login(client, "ingeniero", PASSWORD).status_code == 302

    def test_ten_failures_lock_even_with_correct_password(self, client, engineer):
        fail_login(client, "ingeniero", 10)
        assert is_locked("ingeniero")
        response = login(client, "ingeniero", PASSWORD)
        assert response.status_code == 429
        assert "Cuenta bloqueada" in response.content.decode()

    def test_lock_is_per_account_not_per_ip(self, client, engineer, capturer):
        fail_login(client, "ingeniero", 10)
        assert login(client, "tablerista", PASSWORD).status_code == 302

    def test_lock_lasts_ten_minutes(self, client, engineer):
        fail_login(client, "ingeniero", 10)
        AccessAttempt.objects.filter(username="ingeniero").update(attempt_time=timezone.now() - timedelta(minutes=9))
        assert login(client, "ingeniero", PASSWORD).status_code == 429
        AccessAttempt.objects.filter(username="ingeniero").update(
            attempt_time=timezone.now() - timedelta(minutes=10, seconds=1)
        )
        assert login(client, "ingeniero", PASSWORD).status_code == 302

    def test_admin_can_unlock(self, client, engineer, admin_client):
        fail_login(client, "ingeniero", 10)
        response = admin_client.post(
            reverse("admin:accounts_user_changelist"),
            {"action": "unlock_accounts", "_selected_action": [engineer.pk]},
        )
        assert response.status_code == 302
        assert not is_locked("ingeniero")
        assert login(client, "ingeniero", PASSWORD).status_code == 302


class TestForcedPasswordChange:
    def test_flagged_person_is_redirected_until_changing_password(self, client, engineer):
        engineer.must_change_password = True
        engineer.save()
        client.force_login(engineer)

        response = client.get(reverse("important_variables"))
        assert response.status_code == 302
        assert response.url == reverse("password_change")

        response = client.post(
            reverse("password_change"),
            {"old_password": PASSWORD, "new_password1": "Otra-clave-segura-99", "new_password2": "Otra-clave-segura-99"},
        )
        assert response.status_code == 302
        engineer.refresh_from_db()
        assert not engineer.must_change_password
        assert client.get(reverse("important_variables")).status_code == 200

    def test_logout_is_allowed_while_flagged(self, client, engineer):
        engineer.must_change_password = True
        engineer.save()
        client.force_login(engineer)
        assert client.post(reverse("logout")).url == reverse("login")

    def test_admin_temporary_password_forces_change(self, admin_client, engineer):
        url = reverse("admin:auth_user_password_change", args=[engineer.pk])
        response = admin_client.post(
            url, {"password1": "Temporal-segura-123", "password2": "Temporal-segura-123", "usable_password": "true"}
        )
        assert response.status_code == 302
        engineer.refresh_from_db()
        assert engineer.must_change_password
        assert engineer.check_password("Temporal-segura-123")


class TestAdminUsers:
    def test_only_administrators_use_the_admin(self, admin_client, engineer_client, capturer_client):
        assert admin_client.get(reverse("admin:index")).status_code == 200
        for client in (engineer_client, capturer_client):
            response = client.get(reverse("admin:index"))
            assert response.status_code == 302
            assert reverse("admin:login") in response.url

    def test_people_cannot_be_deleted(self, admin_client, engineer):
        assert admin_client.get(reverse("admin:accounts_user_delete", args=[engineer.pk])).status_code == 403
        assert User.objects.filter(pk=engineer.pk).exists()

    def test_admin_creates_a_capturer_with_forms_and_temporary_password(self, admin_client, biota_form):
        response = admin_client.post(
            reverse("admin:accounts_user_add"),
            {
                "username": "lab1",
                "full_name": "Persona del laboratorio",
                "role": User.Role.CAPTURER,
                "capture_forms": [biota_form.pk],
                "password1": "Temporal-segura-123",
                "password2": "Temporal-segura-123",
            },
        )
        assert response.status_code == 302
        lab = User.objects.get(username="lab1")
        assert lab.must_change_password
        assert list(lab.capture_forms.all()) == [biota_form]


class TestCreateInitialAdmin:
    def test_creates_admin_with_temporary_password(self):
        out = StringIO()
        call_command("create_initial_admin", "sebastian", "Juan Sebastián Rada Rey", stdout=out)
        admin = User.objects.get(username="sebastian")
        password = out.getvalue().split("Contraseña temporal: ")[1].split()[0]
        assert admin.is_admin and admin.must_change_password
        assert admin.check_password(password)

    def test_refuses_existing_username(self, engineer):
        with pytest.raises(CommandError):
            call_command("create_initial_admin", "INGENIERO", "Otra persona")

    def test_from_env_creates_first_admin_once(self, monkeypatch):
        monkeypatch.setenv("PTAR_INITIAL_ADMIN", "sebastian;Juan Sebastián Rada Rey")
        out = StringIO()
        call_command("create_initial_admin", "--from-env", stdout=out)
        assert User.objects.get(username="sebastian").full_name == "Juan Sebastián Rada Rey"
        assert "Contraseña temporal" in out.getvalue()

        # Every later startup is a no-op because an administrator now exists.
        monkeypatch.setenv("PTAR_INITIAL_ADMIN", "otro;Otra Persona")
        out = StringIO()
        call_command("create_initial_admin", "--from-env", stdout=out)
        assert not User.objects.filter(username="otro").exists()
        assert out.getvalue() == ""

    def test_from_env_without_variable_does_nothing(self, monkeypatch):
        monkeypatch.delenv("PTAR_INITIAL_ADMIN", raising=False)
        call_command("create_initial_admin", "--from-env")
        assert not User.objects.exists()


class TestDisplayName:
    @pytest.mark.parametrize(
        "stored, shown",
        [
            ("juan sebastián rada rey", "Juan Sebastián Rada Rey"),
            ("maría de los ángeles gómez", "María de los Ángeles Gómez"),
            ("ana maría pérez-gómez", "Ana María Pérez-Gómez"),
            ("Diana McDonald", "Diana McDonald"),  # capitals typed by hand are kept
        ],
    )
    def test_names_are_shown_capitalized(self, stored, shown):
        assert User(full_name=stored).display_name == shown
