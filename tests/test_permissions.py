"""Who sees what (docs/REQUISITOS.md §4). Checked on the server, whatever the menu shows."""

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db

READING_PAGES = ["important_variables", "explorer", "weekly_charts", "weekly_charts_export"]


class TestHome:
    def test_readers_land_on_the_important_variables(self, admin_client, engineer_client):
        for client in (admin_client, engineer_client):
            assert client.get(reverse("home")).url == reverse("important_variables")

    def test_capturers_land_on_capture(self, capturer_client):
        assert capturer_client.get(reverse("home")).url == reverse("capture_index")


class TestCapturerReadsNothing:
    @pytest.mark.parametrize("page", READING_PAGES)
    def test_reading_pages_are_forbidden_even_by_url(self, capturer_client, page):
        response = capturer_client.get(reverse(page))
        assert response.status_code == 403
        assert "Sin acceso" in response.content.decode()

    def test_menu_only_shows_capture(self, capturer_client):
        page = capturer_client.get(reverse("capture_index")).content.decode()
        assert "Captura" in page
        assert "Variables importantes" not in page and "Explorador" not in page and "ICAV" not in page and "Administración" not in page

    def test_sees_only_their_forms(self, capturer, capturer_client, biota_form, nalco_form):
        capturer.capture_forms.set([biota_form])
        page = capturer_client.get(reverse("capture_index")).content.decode()
        assert "BIOTA Fase I" in page
        assert "Nalco" not in page

    def test_without_forms_still_lands_on_capture(self, capturer_client):
        page = capturer_client.get(reverse("capture_index")).content.decode()
        assert "Todavía no tienes formatos de captura asignados" in page


class TestEngineer:
    @pytest.mark.parametrize("page", READING_PAGES)
    def test_reads_everything(self, engineer_client, page):
        assert engineer_client.get(reverse(page)).status_code == 200

    def test_without_forms_is_read_only(self, engineer_client):
        assert engineer_client.get(reverse("capture_index")).status_code == 403
        page = engineer_client.get(reverse("important_variables")).content.decode()
        assert ">Captura<" not in page

    def test_with_forms_captures_only_in_them(self, engineer, engineer_client, biota_form, nalco_form):
        engineer.capture_forms.set([nalco_form])
        page = engineer_client.get(reverse("capture_index")).content.decode()
        assert "Nalco" in page and "BIOTA Fase I" not in page

    def test_has_no_administration(self, engineer_client):
        page = engineer_client.get(reverse("important_variables")).content.decode()
        assert "Administración" not in page


class TestAdministrator:
    def test_captures_in_every_form(self, admin_client, biota_form, nalco_form):
        page = admin_client.get(reverse("capture_index")).content.decode()
        assert "BIOTA Fase I" in page and "Nalco" in page

    def test_menu_shows_everything(self, admin_client):
        page = admin_client.get(reverse("important_variables")).content.decode()
        for item in ("Variables importantes", "Explorador", "Captura", "Administración"):
            assert item in page


class TestCaching:
    def test_pages_are_private(self, engineer_client):
        # Behind Firebase Hosting a public response would be stored by its CDN and served to others.
        response = engineer_client.get(reverse("important_variables"))
        assert "private" in response["Cache-Control"]

    def test_login_page_is_private_too(self, client):
        assert "private" in client.get(reverse("login"))["Cache-Control"]
