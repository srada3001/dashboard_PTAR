"""Measurements in long format: one row per variable, sampling time and value (docs/REQUISITOS.md §5).

There are no states: a value that does not exist (ND, FS, SB…) has no row. Every creation,
correction or deletion leaves a MeasurementHistory row, and the history is never deleted.
"""

import datetime

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.catalog.models import Variable

from .values import format_number


class TimePrecision(models.TextChoices):
    """How much of the sampling time is known. Hours are never invented: a source that only gives
    the day, or only "a. m." / "p. m.", is stored as such."""

    HOUR = "hour", "Hora exacta"
    AM = "am", "a. m."
    PM = "pm", "p. m."
    DAY = "day", "Solo el día"


# Where each period starts: taken_at holds that instant when the hour is not known.
PERIOD_START = {
    TimePrecision.DAY: datetime.time(0),
    TimePrecision.AM: datetime.time(0),
    TimePrecision.PM: datetime.time(12),
}


def period_start(day, precision):
    """The taken_at of a sample known only by its day, morning or afternoon (Bogotá time)."""
    return timezone.make_aware(datetime.datetime.combine(day, PERIOD_START[precision]))


class Qualifier(models.TextChoices):
    NONE = "", "—"
    BELOW = "<", "<"
    ABOVE = ">", ">"


class Origin(models.TextChoices):
    MANUAL = "manual", "Captura manual"
    HISTORY = "history", "Importación del histórico"
    FILE = "file", "Archivo"
    PI = "pi", "PI"


class Measurement(models.Model):
    variable = models.ForeignKey(Variable, on_delete=models.PROTECT, related_name="measurements", verbose_name="variable")
    taken_at = models.DateTimeField("fecha y hora", help_text="Hora de Bogotá. Sin hora exacta, el inicio del periodo.")
    time_precision = models.CharField("precisión de la hora", max_length=4, choices=TimePrecision.choices)
    value = models.FloatField("valor")
    qualifier = models.CharField(
        "calificador", max_length=1, choices=Qualifier.choices, blank=True,
        help_text="«<0,1»: por debajo de 0,1, normalmente el límite de detección.",
    )
    suspect = models.BooleanField(
        "dudoso", default=False,
        help_text="Valor del histórico fuera del rango físico: no se grafica ni entra en la estadística hasta que alguien lo revise.",
    )
    origin = models.CharField("origen", max_length=10, choices=Origin.choices)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+", verbose_name="registrada por"
    )
    created_at = models.DateTimeField("registrada", auto_now_add=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name="+",
        verbose_name="modificada por",
    )
    updated_at = models.DateTimeField("modificada", auto_now=True)

    class Meta:
        verbose_name = "medición"
        verbose_name_plural = "mediciones"
        ordering = ["-taken_at", "pk"]
        constraints = [
            models.UniqueConstraint(
                fields=["variable", "taken_at"],
                name="measurement_unique",
                violation_error_message="Ya hay un valor de esa variable para esa fecha y hora.",
            ),
        ]
        indexes = [models.Index(fields=["taken_at"], name="measurement_taken_at")]

    def __str__(self):
        return f"{self.variable} · {format_taken_at(self.taken_at, self.time_precision)} · {self.display_value}"

    @property
    def display_value(self):
        return f"{self.qualifier}{format_number(self.value)}"


def format_taken_at(taken_at, precision):
    """'2024-01-03 07:00', '2024-01-03 a. m.' or '2024-01-03'."""
    local = timezone.localtime(taken_at)
    if precision == TimePrecision.HOUR:
        return f"{local:%Y-%m-%d %H:%M}"
    if precision == TimePrecision.DAY:
        return f"{local:%Y-%m-%d}"
    return f"{local:%Y-%m-%d} {TimePrecision(precision).label}"


class HistoryQuerySet(models.QuerySet):
    def delete(self):
        raise PermissionError("El historial de las mediciones nunca se borra.")


class MeasurementHistory(models.Model):
    """One creation, correction or deletion of a measurement. Kept when the measurement is deleted,
    so deleting loses nothing. Never edited or deleted."""

    class Action(models.TextChoices):
        CREATE = "create", "Creó"
        UPDATE = "update", "Corrigió"
        DELETE = "delete", "Borró"

    measurement = models.ForeignKey(
        Measurement, on_delete=models.SET_NULL, null=True, blank=True, related_name="history", verbose_name="medición"
    )
    variable = models.ForeignKey(Variable, on_delete=models.PROTECT, related_name="+", verbose_name="variable")
    taken_at = models.DateTimeField("fecha y hora de la muestra")
    time_precision = models.CharField("precisión de la hora", max_length=4, choices=TimePrecision.choices)
    action = models.CharField("acción", max_length=10, choices=Action.choices)
    old_value = models.FloatField("valor anterior", null=True, blank=True)
    old_qualifier = models.CharField("calificador anterior", max_length=1, blank=True)
    new_value = models.FloatField("valor nuevo", null=True, blank=True)
    new_qualifier = models.CharField("calificador nuevo", max_length=1, blank=True)
    new_suspect = models.BooleanField("dudoso", default=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+", verbose_name="quién")
    timestamp = models.DateTimeField("cuándo", auto_now_add=True)
    reason = models.CharField("motivo", max_length=300, blank=True)
    batch = models.ForeignKey(
        "imports.ImportBatch", on_delete=models.PROTECT, null=True, blank=True, related_name="+",
        verbose_name="lote de importación",
    )

    objects = HistoryQuerySet.as_manager()

    class Meta:
        verbose_name = "historial de una medición"
        verbose_name_plural = "historial de las mediciones"
        ordering = ["-timestamp", "-pk"]
        indexes = [
            models.Index(fields=["variable", "taken_at"], name="history_variable_taken_at"),
            models.Index(fields=["timestamp"], name="history_timestamp"),
        ]

    def __str__(self):
        return f"{self.user} {self.get_action_display().lower()} {self.variable} · {format_taken_at(self.taken_at, self.time_precision)}"

    def delete(self, *args, **kwargs):
        raise PermissionError("El historial de las mediciones nunca se borra.")

    @property
    def change(self):
        """'—' → '7,3' when created, '73' → '7,3' when corrected, '7,3' → '—' when deleted."""
        def shown(value, qualifier):
            return "—" if value is None else f"{qualifier}{format_number(value)}"

        return f"{shown(self.old_value, self.old_qualifier)} → {shown(self.new_value, self.new_qualifier)}"
