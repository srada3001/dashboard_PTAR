import datetime

from django.db import models


class WeeklyExport(models.Model):
    """The file of each Monday with all the data up to the Sunday before (docs/REQUISITOS.md §10).
    The file itself lives in the bucket (exports/), or in the exports/ folder when developing."""

    class Status(models.TextChoices):
        RUNNING = "running", "Preparándose"
        DONE = "done", "Listo"
        FAILED = "failed", "Falló"

    week = models.DateField("semana", unique=True, help_text="El lunes: el archivo trae los datos de antes de ese día.")
    status = models.CharField("estado", max_length=10, choices=Status.choices)
    started_at = models.DateTimeField("empezó")
    finished_at = models.DateTimeField("terminó", null=True, blank=True)
    file_name = models.CharField("archivo", max_length=100, blank=True)
    size = models.PositiveBigIntegerField("tamaño (bytes)", null=True, blank=True)
    measurements = models.PositiveIntegerField("mediciones", null=True, blank=True)
    error = models.TextField("error", blank=True)

    class Meta:
        verbose_name = "exportación semanal"
        verbose_name_plural = "exportaciones semanales"
        ordering = ["-week"]

    def __str__(self):
        return f"Semana del {self.week:%Y-%m-%d}"

    @property
    def last_day(self):
        """The Sunday: the last day whose data the file has."""
        return self.week - datetime.timedelta(days=1)
