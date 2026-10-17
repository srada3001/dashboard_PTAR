from django.contrib import admin

from .models import AuditEntry


@admin.register(AuditEntry)
class AuditEntryAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "actor", "action", "object_type", "object_repr")
    list_filter = ("action", "object_type", "actor")
    search_fields = ("object_repr",)
    date_hierarchy = "timestamp"
    readonly_fields = ("timestamp", "actor", "action", "object_type", "object_id", "object_repr", "changes")

    # Read-only: the log is written by the app.
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
