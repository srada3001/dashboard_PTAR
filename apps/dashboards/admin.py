from django import forms
from django.contrib import admin

from apps.core.audit import AuditedAdmin

from .models import MAX_POINTS, ImportantVariable


class ImportantVariableForm(forms.ModelForm):
    class Meta:
        model = ImportantVariable
        fields = ("parameter", "order", "points")

    def clean_points(self):
        points = self.cleaned_data["points"]
        if len(points) > MAX_POINTS:
            raise forms.ValidationError(
                f"Hasta {MAX_POINTS} puntos: más colores no se distinguen en una gráfica. "
                "Para comparar otros puntos está el Explorador."
            )
        return points


@admin.register(ImportantVariable)
class ImportantVariableAdmin(AuditedAdmin):
    form = ImportantVariableForm
    list_display = ("parameter", "point_list", "order")
    list_editable = ("order",)
    autocomplete_fields = ("parameter",)
    filter_horizontal = ("points",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("parameter").prefetch_related("points")

    @admin.display(description="puntos")
    def point_list(self, obj):
        return ", ".join(str(point) for point in obj.points.all())
