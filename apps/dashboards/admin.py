from django import forms
from django.contrib import admin

from apps.core.audit import AuditedAdmin

from .models import MAX_POINTS, ImportantVariable, ImportantVariableItem, WeeklyChart, WeeklyChartVariable


class SeriesFormSet(forms.BaseInlineFormSet):
    """The series of a chart share its axis, so they share a unit; and one color per point."""

    def clean(self):
        super().clean()
        variables = [
            form.cleaned_data["variable"]
            for form in self.forms
            if form.cleaned_data.get("variable") and not form.cleaned_data.get("DELETE")
        ]
        units = sorted({variable.parameter.unit for variable in variables})
        if len(units) > 1:
            raise forms.ValidationError(
                "Las series de una gráfica comparten el eje, así que tienen la misma unidad; aquí hay "
                + ", ".join(f"«{unit or 'sin unidad'}»" for unit in units) + "."
            )
        if len({variable.point_id for variable in variables}) > MAX_POINTS:
            raise forms.ValidationError(f"Hasta {MAX_POINTS} puntos: más colores no se distinguen en una gráfica.")


class ImportantVariableItemInline(admin.TabularInline):
    model = ImportantVariableItem
    formset = SeriesFormSet
    extra = 0
    autocomplete_fields = ("variable",)
    fields = ("order", "variable")


@admin.register(ImportantVariable)
class ImportantVariableAdmin(AuditedAdmin):
    list_display = ("title", "series_count", "order")
    list_editable = ("order",)
    search_fields = ("title",)
    inlines = [ImportantVariableItemInline]

    @admin.display(description="series")
    def series_count(self, obj):
        return obj.items.count()


class WeeklyChartVariableInline(admin.TabularInline):
    model = WeeklyChartVariable
    formset = SeriesFormSet
    extra = 0
    autocomplete_fields = ("variable",)
    fields = ("order", "variable")


@admin.register(WeeklyChart)
class WeeklyChartAdmin(AuditedAdmin):
    list_display = ("title", "series_count", "order")
    list_editable = ("order",)
    search_fields = ("title",)
    inlines = [WeeklyChartVariableInline]

    @admin.display(description="series")
    def series_count(self, obj):
        return obj.items.count()
