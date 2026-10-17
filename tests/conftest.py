import pytest
from django.test import Client

from apps.accounts.models import User
from apps.catalog.models import CaptureForm, CaptureFormVariable, Parameter, ProcessArea, SamplingPoint, Source, Variable

PASSWORD = "Clave-de-prueba-2026"


def make_client(user):
    client = Client()
    client.force_login(user)
    return client


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser("admin", "Administrador", PASSWORD)


@pytest.fixture
def engineer(db):
    return User.objects.create_user(
        "ingeniero", "Laura Gómez", PASSWORD, role=User.Role.ENGINEER, must_change_password=False
    )


@pytest.fixture
def capturer(db):
    return User.objects.create_user(
        "tablerista", "Carlos Pérez", PASSWORD, role=User.Role.CAPTURER, must_change_password=False
    )


@pytest.fixture
def admin_client(admin_user):
    return make_client(admin_user)


@pytest.fixture
def engineer_client(engineer):
    return make_client(engineer)


@pytest.fixture
def capturer_client(capturer):
    return make_client(capturer)


@pytest.fixture
def biota(db):
    return Source.objects.create(code="BIOTA", name="BIOTA")


@pytest.fixture
def nalco(db):
    return Source.objects.create(code="Nalco", name="Nalco (aliado químico)")


@pytest.fixture
def outlet(db):
    area = ProcessArea.objects.create(name="Vertimiento", order=5)
    return SamplingPoint.objects.create(code="BA-4010", name="Vertedero, salida al río", area=area)


@pytest.fixture
def phenols(db):
    return Parameter.objects.create(code="Fenoles", name="Fenoles", unit="mg/L")


@pytest.fixture
def ph(db):
    return Parameter.objects.create(code="pH", name="pH", physical_min=0, physical_max=14)


@pytest.fixture
def phenols_biota(outlet, phenols, biota):
    return Variable.objects.create(point=outlet, parameter=phenols, source=biota)


@pytest.fixture
def biota_form(biota, phenols_biota):
    form = CaptureForm.objects.create(name="BIOTA Fase I", source=biota)
    CaptureFormVariable.objects.create(form=form, variable=phenols_biota, order=1)
    return form


@pytest.fixture
def nalco_form(nalco):
    return CaptureForm.objects.create(name="Nalco", source=nalco)
