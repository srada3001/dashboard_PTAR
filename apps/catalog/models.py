"""Catalogs: what is measured, where, by whom, against which limits, and in which capture forms.

All of this is data edited in the admin, never constants in the code: adding a sampling point, a
parameter or a limit needs no programming (docs/REQUISITOS.md §5).
"""

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q
from django.db.models.functions import Lower


class Schedule(models.TextChoices):
    """How often a variable is sampled, and the shape of a capture form. A variable's frequency
    gives its cells in the capture: one per hour, 07:00 and 16:00, a. m. and p. m., or one per day."""

    HOURLY = "hourly", "Cada hora"
    TWICE_DAILY = "twice_daily", "7 a. m. y 4 p. m."
    AM_PM = "am_pm", "a. m. y p. m."
    DAILY = "daily", "Diaria"
    OCCASIONAL = "occasional", "Eventual"


def unique_ignoring_case(field, name, message):
    """Catalog names are unique regardless of case: "ba-4010" duplicates "BA-4010"."""
    return models.UniqueConstraint(Lower(field), name=name, violation_error_message=message)


def ordered_range(low, high, name, message):
    """An optional range: either end may be missing, but when both are set, low < high."""
    return models.CheckConstraint(
        condition=Q(**{f"{low}__isnull": True}) | Q(**{f"{high}__isnull": True}) | Q(**{f"{low}__lt": F(high)}),
        name=name,
        violation_error_message=message,
    )


class StrippedNamesMixin:
    """Leading and trailing spaces are removed from names, so "BA-4010 " does not duplicate "BA-4010"."""

    stripped_fields = ()

    def clean(self):
        super().clean()
        for field in self.stripped_fields:
            value = getattr(self, field)
            if isinstance(value, str):
                setattr(self, field, value.strip())


class Source(StrippedNamesMixin, models.Model):
    """Who measured: Labviewer, BIOTA, Nalco, PI… Not who typed the value in."""

    code = models.CharField("código", max_length=30, help_text="Nombre corto: Labviewer, BIOTA, Nalco, PI.")
    name = models.CharField("nombre", max_length=100, help_text="Por ejemplo, «Laboratorio central».")
    description = models.TextField("descripción", blank=True)

    stripped_fields = ("code", "name")

    class Meta:
        verbose_name = "fuente"
        verbose_name_plural = "fuentes"
        ordering = [Lower("code")]
        constraints = [unique_ignoring_case("code", "source_code_unique", "Ya existe una fuente con ese código.")]

    def __str__(self):
        return self.code


class ProcessArea(StrippedNamesMixin, models.Model):
    """A zone of the plant that groups sampling points (entry, primary treatment, Fase I…)."""

    name = models.CharField("nombre", max_length=100)
    order = models.PositiveSmallIntegerField("orden", default=0, help_text="Orden en que se presentan las zonas.")

    stripped_fields = ("name",)

    class Meta:
        verbose_name = "zona"
        verbose_name_plural = "zonas"
        ordering = ["order", Lower("name")]
        constraints = [unique_ignoring_case("name", "processarea_name_unique", "Ya existe una zona con ese nombre.")]

    def __str__(self):
        return self.name


class SamplingPoint(StrippedNamesMixin, models.Model):
    code = models.CharField("código", max_length=30, help_text="Código canónico, por ejemplo «BA-4010».")
    name = models.CharField("descripción", max_length=150, blank=True, help_text="Por ejemplo, «Vertedero, salida al río».")
    area = models.ForeignKey(
        ProcessArea, on_delete=models.PROTECT, null=True, blank=True, related_name="points", verbose_name="zona"
    )
    order = models.PositiveSmallIntegerField("orden", default=0, help_text="Orden dentro de su zona.")
    is_active = models.BooleanField("activo", default=True, help_text="Desmarcar en lugar de borrar cuando ya no se muestrea.")

    stripped_fields = ("code", "name")

    class Meta:
        verbose_name = "punto de muestreo"
        verbose_name_plural = "puntos de muestreo"
        ordering = ["area__order", "order", Lower("code")]
        constraints = [unique_ignoring_case("code", "samplingpoint_code_unique", "Ya existe un punto con ese código.")]

    def __str__(self):
        return self.code


class PointAlias(StrippedNamesMixin, models.Model):
    """Other spellings of a point found in the spreadsheets ("BA4010", "VERTEDERO BA4010"),
    used to map the historical columns (phase 1)."""

    point = models.ForeignKey(SamplingPoint, on_delete=models.CASCADE, related_name="aliases", verbose_name="punto")
    alias = models.CharField("alias", max_length=60)

    stripped_fields = ("alias",)

    class Meta:
        verbose_name = "alias"
        verbose_name_plural = "alias"
        ordering = [Lower("alias")]
        constraints = [unique_ignoring_case("alias", "pointalias_alias_unique", "Ese alias ya está asignado a un punto.")]

    def __str__(self):
        return self.alias


class Parameter(StrippedNamesMixin, models.Model):
    code = models.CharField("código", max_length=30, help_text="Nombre corto: «Fenoles», «SST», «G&A», «pH».")
    name = models.CharField("nombre", max_length=150, help_text="Nombre completo, por ejemplo «Sólidos suspendidos totales».")
    unit = models.CharField("unidad", max_length=30, blank=True, help_text="Por ejemplo «mg/L» o «°C»; vacío si no tiene.")
    decimals = models.PositiveSmallIntegerField("decimales", default=2, help_text="Decimales con que se muestran los valores.")
    physical_min = models.FloatField(
        "mínimo físico", null=True, blank=True, help_text="Opcional. Un valor por debajo es imposible y se rechaza."
    )
    physical_max = models.FloatField(
        "máximo físico", null=True, blank=True, help_text="Opcional. Un valor por encima es imposible y se rechaza."
    )
    is_active = models.BooleanField("activo", default=True)

    stripped_fields = ("code", "name", "unit")

    class Meta:
        verbose_name = "parámetro"
        verbose_name_plural = "parámetros"
        ordering = [Lower("code")]
        constraints = [
            unique_ignoring_case("code", "parameter_code_unique", "Ya existe un parámetro con ese código."),
            ordered_range(
                "physical_min", "physical_max", "parameter_physical_range",
                "El mínimo físico debe ser menor que el máximo físico.",
            ),
        ]

    def __str__(self):
        return self.code


class Variable(models.Model):
    """Point + parameter + source: what is captured, imported and plotted.

    The same parameter at the same point measured by two sources is two variables, and both are
    kept: no source replaces another.
    """

    point = models.ForeignKey(SamplingPoint, on_delete=models.PROTECT, related_name="variables", verbose_name="punto")
    parameter = models.ForeignKey(Parameter, on_delete=models.PROTECT, related_name="variables", verbose_name="parámetro")
    source = models.ForeignKey(Source, on_delete=models.PROTECT, related_name="variables", verbose_name="fuente")
    typical_min = models.FloatField(
        "mínimo habitual", null=True, blank=True, help_text="Opcional. Por debajo, la captura pide confirmar el valor."
    )
    typical_max = models.FloatField(
        "máximo habitual", null=True, blank=True, help_text="Opcional. Por encima, la captura pide confirmar el valor."
    )
    time_resolution = models.CharField("frecuencia", max_length=20, choices=Schedule.choices, default=Schedule.DAILY)

    class Meta:
        verbose_name = "variable"
        verbose_name_plural = "variables"
        ordering = ["point__area__order", "point__order", Lower("point__code"), Lower("parameter__code"), Lower("source__code")]
        constraints = [
            models.UniqueConstraint(
                fields=["point", "parameter", "source"],
                name="variable_unique",
                violation_error_message="Ya existe una variable con ese punto, parámetro y fuente.",
            ),
            ordered_range(
                "typical_min", "typical_max", "variable_typical_range",
                "El mínimo habitual debe ser menor que el máximo habitual.",
            ),
        ]

    def __str__(self):
        return f"{self.point} · {self.parameter} · {self.source}"

    def clean(self):
        super().clean()
        if not self.parameter_id:
            return
        low, high = self.parameter.physical_min, self.parameter.physical_max
        errors = {}
        for field in ("typical_min", "typical_max"):
            value = getattr(self, field)
            if value is None:
                continue
            if (low is not None and value < low) or (high is not None and value > high):
                errors[field] = "Está fuera del rango físico del parámetro."
        if errors:
            raise ValidationError(errors)


class LimitQuerySet(models.QuerySet):
    def in_force(self, on_date):
        """Limits valid on a date. An empty start or end means it has no bound on that side."""
        return self.filter(
            Q(valid_from__isnull=True) | Q(valid_from__lte=on_date),
            Q(valid_to__isnull=True) | Q(valid_to__gte=on_date),
        )


class Limit(models.Model):
    """A limit for a point and parameter, for every source. Each sample is checked against the
    limit in force on its date, so limits are never edited in place when they change: the old one
    gets an end date and a new one starts."""

    class Kind(models.TextChoices):
        DISCHARGE = "discharge", "Límite de vertimiento"
        DESIGN = "design", "Máximo de diseño en la entrada"
        OPERATING = "operating", "Ventana operativa"
        OTHER = "other", "Otro"

    point = models.ForeignKey(SamplingPoint, on_delete=models.PROTECT, related_name="limits", verbose_name="punto")
    parameter = models.ForeignKey(Parameter, on_delete=models.PROTECT, related_name="limits", verbose_name="parámetro")
    kind = models.CharField("tipo", max_length=20, choices=Kind.choices)
    min_value = models.FloatField("mínimo", null=True, blank=True, help_text="Vacío si el límite solo tiene máximo.")
    max_value = models.FloatField("máximo", null=True, blank=True, help_text="Vacío si el límite solo tiene mínimo.")
    valid_from = models.DateField("vigente desde", null=True, blank=True, help_text="Vacío: desde siempre.")
    valid_to = models.DateField("vigente hasta", null=True, blank=True, help_text="Vacío: sigue vigente.")
    reference = models.CharField("referencia", max_length=200, blank=True, help_text="De dónde sale el límite.")

    objects = LimitQuerySet.as_manager()

    class Meta:
        verbose_name = "límite"
        verbose_name_plural = "límites"
        ordering = [Lower("point__code"), Lower("parameter__code"), "kind", "valid_from"]
        constraints = [
            models.CheckConstraint(
                condition=Q(min_value__isnull=False) | Q(max_value__isnull=False),
                name="limit_has_a_bound",
                violation_error_message="Un límite necesita un mínimo, un máximo o ambos.",
            ),
            ordered_range("min_value", "max_value", "limit_range", "El mínimo debe ser menor que el máximo."),
            models.CheckConstraint(
                condition=Q(valid_from__isnull=True) | Q(valid_to__isnull=True) | Q(valid_from__lte=F("valid_to")),
                name="limit_validity_order",
                violation_error_message="La fecha de inicio debe ser anterior a la de fin.",
            ),
        ]

    def __str__(self):
        return f"{self.point} · {self.parameter} · {self.get_kind_display()}"

    def clean(self):
        super().clean()
        if not (self.point_id and self.parameter_id and self.kind):
            return
        others = Limit.objects.filter(point=self.point_id, parameter=self.parameter_id, kind=self.kind).exclude(pk=self.pk)
        # Two periods overlap unless one ends before the other starts; a missing date is unbounded.
        if self.valid_to is not None:
            others = others.filter(Q(valid_from__isnull=True) | Q(valid_from__lte=self.valid_to))
        if self.valid_from is not None:
            others = others.filter(Q(valid_to__isnull=True) | Q(valid_to__gte=self.valid_from))
        if others.exists():
            raise ValidationError(
                "Ya hay un límite del mismo tipo para ese punto y parámetro en esas fechas. "
                "Ponle fecha de fin al anterior antes de crear el nuevo."
            )


class CaptureForm(StrippedNamesMixin, models.Model):
    """The variables of one source that are typed in together, like one sheet of today's Excel."""

    name = models.CharField("nombre", max_length=100)
    source = models.ForeignKey(Source, on_delete=models.PROTECT, related_name="capture_forms", verbose_name="fuente")
    schedule = models.CharField("forma", max_length=20, choices=Schedule.choices, default=Schedule.DAILY)
    variables = models.ManyToManyField(Variable, through="CaptureFormVariable", related_name="capture_forms")

    stripped_fields = ("name",)

    class Meta:
        verbose_name = "formato de captura"
        verbose_name_plural = "formatos de captura"
        ordering = [Lower("name")]
        constraints = [unique_ignoring_case("name", "captureform_name_unique", "Ya existe un formato con ese nombre.")]

    def __str__(self):
        return self.name


class CaptureFormVariable(models.Model):
    form = models.ForeignKey(CaptureForm, on_delete=models.CASCADE, related_name="items", verbose_name="formato")
    variable = models.ForeignKey(Variable, on_delete=models.PROTECT, related_name="+", verbose_name="variable")
    order = models.PositiveSmallIntegerField("orden", default=0)

    class Meta:
        verbose_name = "variable del formato"
        verbose_name_plural = "variables del formato"
        ordering = ["order", "pk"]
        constraints = [
            models.UniqueConstraint(
                fields=["form", "variable"],
                name="captureformvariable_unique",
                violation_error_message="La variable ya está en el formato.",
            ),
        ]

    def __str__(self):
        return str(self.variable)

    def clean(self):
        super().clean()
        # The form may still be unsaved (admin "add" page), so go through the relations, not the ids.
        try:
            form, variable = self.form, self.variable
        except (CaptureForm.DoesNotExist, Variable.DoesNotExist):
            return
        if form.source_id and variable.source_id != form.source_id:
            raise ValidationError({"variable": f"Es de la fuente {variable.source}; el formato es de {form.source}."})
