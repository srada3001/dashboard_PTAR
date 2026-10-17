from django.conf import settings
from django.db import models


class AuditEntry(models.Model):
    """Who changed what and when in users, catalogs, ranges and limits. `changes` maps each field
    to [before, after] as shown to people. Measurements have their own history (phase 1)."""

    class Action(models.TextChoices):
        CREATE = "create", "Creó"
        UPDATE = "update", "Modificó"
        DELETE = "delete", "Borró"

    timestamp = models.DateTimeField("fecha", auto_now_add=True)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+", verbose_name="quién"
    )
    action = models.CharField("acción", max_length=10, choices=Action.choices)
    object_type = models.CharField("tipo", max_length=50)
    object_id = models.PositiveBigIntegerField("id")
    object_repr = models.CharField("objeto", max_length=200)
    changes = models.JSONField("cambios", default=dict, blank=True)

    class Meta:
        verbose_name = "registro de auditoría"
        verbose_name_plural = "registro de auditoría"
        ordering = ["-timestamp", "-pk"]

    def __str__(self):
        return f"{self.actor} {self.get_action_display().lower()} {self.object_type} {self.object_repr}"

    @classmethod
    def record(cls, actor, action, obj, changes=None):
        return cls.objects.create(
            actor=actor,
            action=action,
            object_type=str(obj._meta.verbose_name),
            object_id=obj.pk,
            object_repr=str(obj)[:200],
            changes=changes or {},
        )
