from django.contrib import admin

from apps.core.audit import AuditedAdmin

from .models import (
    CaptureForm,
    CaptureFormVariable,
    Limit,
    Parameter,
    PointAlias,
    ProcessArea,
    SamplingPoint,
    Source,
    Variable,
)


def range_text(low, high, unit=""):
    if low is None and high is None:
        return "—"
    unit = f" {unit}" if unit else ""
    if low is None:
        return f"≤ {high:g}{unit}"
    if high is None:
        return f"≥ {low:g}{unit}"
    return f"{low:g} – {high:g}{unit}"


@admin.register(Source)
class SourceAdmin(AuditedAdmin):
    list_display = ("code", "name")
    search_fields = ("code", "name")


@admin.register(ProcessArea)
class ProcessAreaAdmin(AuditedAdmin):
    list_display = ("name", "order")
    list_editable = ("order",)
    search_fields = ("name",)


class PointAliasInline(admin.TabularInline):
    model = PointAlias
    extra = 0


@admin.register(SamplingPoint)
class SamplingPointAdmin(AuditedAdmin):
    list_display = ("code", "name", "area", "order", "is_active")
    list_filter = ("area", "is_active")
    search_fields = ("code", "name", "aliases__alias")
    inlines = [PointAliasInline]


@admin.register(Parameter)
class ParameterAdmin(AuditedAdmin):
    list_display = ("code", "name", "unit", "physical_range", "is_active")
    list_filter = ("is_active",)
    search_fields = ("code", "name")
    fieldsets = (
        (None, {"fields": ("code", "name", "unit", "decimals", "is_active")}),
        (
            "Rango físico (opcional)",
            {
                "description": "Lo que queda fuera es imposible y la captura lo rechaza. "
                "Sin rango, basta con que el valor sea un número.",
                "fields": (("physical_min", "physical_max"),),
            },
        ),
    )

    @admin.display(description="rango físico")
    def physical_range(self, obj):
        return range_text(obj.physical_min, obj.physical_max, obj.unit)


@admin.register(Variable)
class VariableAdmin(AuditedAdmin):
    list_display = ("point", "parameter", "source", "time_resolution", "typical_range")
    list_filter = ("source", "parameter", "point__area", "time_resolution")
    search_fields = ("point__code", "parameter__code", "parameter__name", "source__code")
    autocomplete_fields = ("point", "parameter", "source")
    list_select_related = ("point", "parameter", "source")
    fieldsets = (
        (None, {"fields": ("point", "parameter", "source", "time_resolution")}),
        (
            "Rango habitual (opcional)",
            {
                "description": "Fuera de él, la captura pide confirmar el valor antes de guardarlo.",
                "fields": (("typical_min", "typical_max"),),
            },
        ),
    )

    @admin.display(description="rango habitual")
    def typical_range(self, obj):
        return range_text(obj.typical_min, obj.typical_max, obj.parameter.unit)


@admin.register(Limit)
class LimitAdmin(AuditedAdmin):
    list_display = ("point", "parameter", "kind", "bounds", "valid_from", "valid_to", "reference")
    list_filter = ("kind", "parameter", "point")
    search_fields = ("point__code", "parameter__code", "reference")
    autocomplete_fields = ("point", "parameter")
    list_select_related = ("point", "parameter")
    fieldsets = (
        (None, {"fields": ("point", "parameter", "kind", ("min_value", "max_value"), "reference")}),
        (
            "Vigencia",
            {
                "description": "Cada muestra se evalúa con el límite vigente en su fecha. Cuando un límite "
                "cambia, se le pone fecha de fin al anterior y se crea uno nuevo.",
                "fields": (("valid_from", "valid_to"),),
            },
        ),
    )

    @admin.display(description="valor")
    def bounds(self, obj):
        return range_text(obj.min_value, obj.max_value, obj.parameter.unit)


class CaptureFormVariableInline(admin.TabularInline):
    model = CaptureFormVariable
    extra = 0
    autocomplete_fields = ("variable",)
    fields = ("order", "variable")


@admin.register(CaptureForm)
class CaptureFormAdmin(AuditedAdmin):
    list_display = ("name", "source", "schedule", "variable_count")
    list_filter = ("source", "schedule")
    search_fields = ("name",)
    inlines = [CaptureFormVariableInline]

    @admin.display(description="variables")
    def variable_count(self, obj):
        return obj.items.count()
