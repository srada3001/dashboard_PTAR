from django.contrib import admin

from .models import Measurement, MeasurementHistory, format_taken_at


@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    """Read-only: values are corrected in the capture, which keeps their history."""

    list_display = ("variable", "when", "shown_value", "suspect", "origin", "created_by")
    list_filter = ("suspect", "origin", "time_precision", "variable__source", "variable__parameter", "variable__point")
    search_fields = ("variable__point__code", "variable__parameter__code", "variable__source__code")
    date_hierarchy = "taken_at"
    list_select_related = ("variable__point", "variable__parameter", "variable__source", "created_by")
    show_full_result_count = False

    @admin.display(description="fecha", ordering="taken_at")
    def when(self, obj):
        return format_taken_at(obj.taken_at, obj.time_precision)

    @admin.display(description="valor", ordering="value")
    def shown_value(self, obj):
        return obj.display_value

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(MeasurementHistory)
class MeasurementHistoryAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "user", "action", "variable", "when", "change", "reason", "batch")
    list_filter = ("action", "user", "variable__source", "variable__parameter")
    search_fields = ("variable__point__code", "variable__parameter__code", "reason")
    date_hierarchy = "timestamp"
    show_full_result_count = False

    def get_queryset(self, request):
        # The batch's report is large: joined into every row, it made the page take minutes.
        return (
            super().get_queryset(request)
            .select_related("variable__point", "variable__parameter", "variable__source", "user", "batch")
            .defer("batch__report", "batch__counts")
        )

    @admin.display(description="fecha de la muestra", ordering="taken_at")
    def when(self, obj):
        return format_taken_at(obj.taken_at, obj.time_precision)

    @admin.display(description="cambio")
    def change(self, obj):
        return obj.change

    # The history is never edited or deleted.
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
