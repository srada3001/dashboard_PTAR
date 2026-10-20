from django.contrib import admin

from .models import WeeklyExport


@admin.register(WeeklyExport)
class WeeklyExportAdmin(admin.ModelAdmin):
    """Read-only: the app prepares each week's file by itself (Exportaciones shows and serves them)."""

    list_display = ("week", "status", "started_at", "finished_at", "measurements", "size", "file_name")
    list_filter = ("status",)
    readonly_fields = [field.name for field in WeeklyExport._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
