"""What the reading views show. Like the catalogs, it is data edited in the admin: adding a point to
a chart needs no programming (CLAUDE.md)."""

from django.db import models

from apps.catalog.models import Parameter, SamplingPoint

# One color per point on a chart; past eight, colors can no longer be told apart.
MAX_POINTS = 8


class ImportantVariable(models.Model):
    """One card of «Variables importantes» (docs/REQUISITOS.md §7.1): a parameter at chosen points,
    with every source that measures it there."""

    parameter = models.OneToOneField(
        Parameter, on_delete=models.PROTECT, related_name="+", verbose_name="parámetro"
    )
    points = models.ManyToManyField(
        SamplingPoint,
        related_name="+",
        verbose_name="puntos",
        help_text=f"Los puntos que se grafican, hasta {MAX_POINTS} (uno por color). Se muestran todas las "
        "fuentes que miden el parámetro en ellos. Para comparar otros puntos está el Explorador.",
    )
    order = models.PositiveSmallIntegerField("orden", default=0, help_text="Orden en que se presentan.")

    class Meta:
        verbose_name = "variable importante"
        verbose_name_plural = "variables importantes"
        ordering = ["order", "pk"]

    def __str__(self):
        return self.parameter.name
