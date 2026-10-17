from datetime import date

import pytest
from django.core.exceptions import ValidationError

from apps.catalog.models import (
    CaptureFormVariable,
    Limit,
    Parameter,
    PointAlias,
    SamplingPoint,
    Source,
    Variable,
)

pytestmark = pytest.mark.django_db


class TestNames:
    def test_codes_are_unique_ignoring_case(self, outlet, phenols, biota):
        for duplicate in (
            SamplingPoint(code="ba-4010"),
            Parameter(code="FENOLES", name="Fenoles"),
            Source(code="biota", name="Otra"),
        ):
            with pytest.raises(ValidationError, match="Ya existe"):
                duplicate.full_clean()

    def test_surrounding_spaces_do_not_make_a_new_name(self, outlet):
        with pytest.raises(ValidationError, match="Ya existe un punto"):
            SamplingPoint(code=" BA-4010 ").full_clean()

    def test_an_alias_belongs_to_one_point(self, outlet):
        PointAlias.objects.create(point=outlet, alias="BA4010")
        other = SamplingPoint.objects.create(code="BA-4001")
        with pytest.raises(ValidationError, match="Ese alias ya está asignado"):
            PointAlias(point=other, alias="ba4010").full_clean()


class TestRanges:
    def test_ranges_are_optional(self, outlet, biota):
        parameter = Parameter(code="SST", name="Sólidos suspendidos totales", unit="mg/L")
        parameter.full_clean()
        parameter.save()
        Variable(point=outlet, parameter=parameter, source=biota).full_clean()

    def test_one_sided_ranges_are_allowed(self):
        Parameter(code="SST", name="SST", physical_min=0).full_clean()

    def test_physical_minimum_below_maximum(self):
        with pytest.raises(ValidationError, match="El mínimo físico debe ser menor"):
            Parameter(code="pH", name="pH", physical_min=14, physical_max=0).full_clean()

    def test_typical_minimum_below_maximum(self, outlet, phenols, biota):
        with pytest.raises(ValidationError, match="El mínimo habitual debe ser menor"):
            Variable(point=outlet, parameter=phenols, source=biota, typical_min=2, typical_max=1).full_clean()

    def test_typical_range_inside_the_physical_range(self, outlet, ph, biota):
        with pytest.raises(ValidationError, match="fuera del rango físico"):
            Variable(point=outlet, parameter=ph, source=biota, typical_min=6, typical_max=15).full_clean()


class TestVariables:
    def test_one_variable_per_point_parameter_and_source(self, phenols_biota, outlet, phenols, biota):
        with pytest.raises(ValidationError, match="Ya existe una variable"):
            Variable(point=outlet, parameter=phenols, source=biota).full_clean()

    def test_two_sources_of_the_same_thing_coexist(self, phenols_biota, outlet, phenols, nalco):
        Variable(point=outlet, parameter=phenols, source=nalco).full_clean()

    def test_shown_as_point_parameter_source(self, phenols_biota):
        assert str(phenols_biota) == "BA-4010 · Fenoles · BIOTA"


class TestLimits:
    def limit(self, point, parameter, **fields):
        fields.setdefault("kind", Limit.Kind.DISCHARGE)
        return Limit(point=point, parameter=parameter, **fields)

    def test_needs_a_bound(self, outlet, phenols):
        with pytest.raises(ValidationError, match="necesita un mínimo, un máximo o ambos"):
            self.limit(outlet, phenols).full_clean()

    def test_a_window_needs_minimum_below_maximum(self, outlet, ph):
        with pytest.raises(ValidationError, match="El mínimo debe ser menor"):
            self.limit(outlet, ph, min_value=8.5, max_value=6.4).full_clean()

    def test_dates_in_order(self, outlet, phenols):
        with pytest.raises(ValidationError, match="La fecha de inicio debe ser anterior"):
            self.limit(outlet, phenols, max_value=0.2, valid_from=date(2026, 2, 1), valid_to=date(2026, 1, 1)).full_clean()

    def test_overlapping_periods_of_the_same_kind_are_rejected(self, outlet, phenols):
        self.limit(outlet, phenols, max_value=0.2, valid_from=date(2026, 1, 1)).save()
        with pytest.raises(ValidationError, match="Ya hay un límite del mismo tipo"):
            self.limit(outlet, phenols, max_value=0.1, valid_from=date(2026, 6, 1)).full_clean()

    def test_a_new_limit_after_closing_the_old_one(self, outlet, phenols):
        self.limit(outlet, phenols, max_value=0.2, valid_to=date(2026, 5, 31)).save()
        self.limit(outlet, phenols, max_value=0.1, valid_from=date(2026, 6, 1)).full_clean()

    def test_different_kinds_may_overlap(self, outlet, phenols):
        self.limit(outlet, phenols, max_value=0.2).save()
        self.limit(outlet, phenols, max_value=0.15, kind=Limit.Kind.OPERATING).full_clean()

    def test_the_limit_in_force_on_a_date(self, outlet, phenols):
        old = self.limit(outlet, phenols, max_value=0.2, valid_to=date(2026, 5, 31))
        new = self.limit(outlet, phenols, max_value=0.1, valid_from=date(2026, 6, 1))
        old.save()
        new.save()
        assert list(Limit.objects.in_force(date(2026, 5, 31))) == [old]
        assert list(Limit.objects.in_force(date(2026, 6, 1))) == [new]


class TestCaptureForms:
    def test_variables_must_be_of_the_form_source(self, nalco_form, phenols_biota):
        with pytest.raises(ValidationError, match="Es de la fuente BIOTA; el formato es de Nalco"):
            CaptureFormVariable(form=nalco_form, variable=phenols_biota).full_clean()

    def test_a_variable_appears_once_per_form(self, biota_form, phenols_biota):
        with pytest.raises(ValidationError, match="La variable ya está en el formato"):
            CaptureFormVariable(form=biota_form, variable=phenols_biota).full_clean()
