from django.conf import settings
from django.db import models


class ImportBatch(models.Model):
    """One run of the historical import over one Excel table, with its counts and report
    (docs/REQUISITOS.md §9). Dry runs are kept too, so their report can be reviewed."""

    file_name = models.CharField("archivo", max_length=255)
    file_sha256 = models.CharField("huella del archivo", max_length=64)
    sheet = models.CharField("hoja", max_length=100)
    table = models.CharField("tabla de Excel", max_length=100)
    dry_run = models.BooleanField("en seco", help_text="Simulación: no guardó nada.")
    run_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+", verbose_name="quién")
    started_at = models.DateTimeField("inicio")
    finished_at = models.DateTimeField("fin")
    counts = models.JSONField("conteos", default=dict)
    report = models.JSONField("informe", default=dict)

    class Meta:
        verbose_name = "lote de importación"
        verbose_name_plural = "lotes de importación"
        ordering = ["-started_at", "-pk"]

    def __str__(self):
        mode = " (en seco)" if self.dry_run else ""
        return f"{self.table} · {self.started_at:%Y-%m-%d %H:%M}{mode}"
