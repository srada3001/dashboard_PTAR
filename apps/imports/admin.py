from django.contrib import admin
from django.template.loader import render_to_string

from .models import ImportBatch

COUNT_LABELS = [
    ("rows", "Filas de la tabla"),
    ("imported", "Mediciones importadas"),
    ("already_present", "Ya estaban en la base, iguales"),
    ("existing_conflicts", "Ya estaban con otro valor (no se tocaron)"),
    ("suspect", "Dudosas: fuera del rango físico"),
    ("qualified", "Con calificador (< o >)"),
    ("text_numbers", "Números escritos como texto"),
    ("nan", "No numéricos: NaN, no se importan"),
    ("formula_cells", "Celdas con fórmula: no se importan"),
    ("identical_duplicates", "Duplicados iguales: se importan una vez"),
    ("conflicts", "Duplicados con valores distintos: no se importa ninguno"),
    ("conflict_values", "Valores de esos duplicados"),
    ("rounded_times", "Filas con la hora redondeada (06:59 → 07:00)"),
    ("deduced_times", "Filas con la hora deducida por la secuencia"),
    ("dropped_rows", "Filas sin fecha válida: no se importan"),
    ("dropped_values", "Valores de esas filas"),
    ("skipped_columns", "Columnas omitidas"),
    ("variables_created", "Variables creadas"),
    ("catalog_created", "Entradas del catálogo creadas"),
]

SECTIONS = [
    ("suspect_values", "Dudosas: fuera del rango físico", [("row", "Fila"), ("taken_at", "Fecha"), ("header", "Columna"), ("value", "Valor"), ("range", "Rango físico")]),
    ("conflicts", "Duplicados con valores distintos (no se importó ninguno)", [("variable", "Variable"), ("taken_at", "Fecha"), ("values", "Valores")]),
    ("existing_conflicts", "Ya estaban en la base con otro valor", [("row", "Fila"), ("variable", "Variable"), ("taken_at", "Fecha"), ("existing", "En la base"), ("new", "En el archivo")]),
    ("dropped_rows", "Filas sin fecha válida (no se importaron)", [("row", "Fila"), ("date", "Fecha escrita"), ("reason", "Motivo"), ("values", "Valores")]),
    ("deduced_times", "Horas deducidas por la secuencia", [("row", "Fila"), ("written", "Escrita"), ("deduced", "Deducida")]),
    ("nan_values", "No numéricos (NaN)", [("row", "Fila"), ("date", "Fecha"), ("header", "Columna"), ("value", "Valor")]),
    ("qualified_values", "Con calificador", [("row", "Fila"), ("taken_at", "Fecha"), ("header", "Columna"), ("value", "Valor")]),
]


@admin.register(ImportBatch)
class ImportBatchAdmin(admin.ModelAdmin):
    list_display = ("table", "sheet", "file_name", "started_at", "dry_run", "run_by", "imported", "suspect", "nan")
    list_filter = ("dry_run", "table")
    fields = ("file_name", "file_sha256", "sheet", "table", "dry_run", "run_by", "started_at", "finished_at", "report_view")
    readonly_fields = fields

    @admin.display(description="importadas")
    def imported(self, obj):
        return obj.counts.get("imported", 0)

    @admin.display(description="dudosas")
    def suspect(self, obj):
        return obj.counts.get("suspect", 0)

    @admin.display(description="NaN")
    def nan(self, obj):
        return obj.counts.get("nan", 0)

    @admin.display(description="informe")
    def report_view(self, obj):
        report = obj.report or {}
        sections = []
        for key, title, columns in SECTIONS:
            items = report.get(key) or []
            rows = []
            for item in items:
                cells = []
                for field, _ in columns:
                    value = item.get(field, "")
                    if field == "values" and isinstance(value, list):
                        value = " · ".join(f"fila {v['row']}, {v['header']}: {v['value']}" for v in value)
                    cells.append(value)
                rows.append(cells)
            sections.append({"title": title, "headers": [label for _, label in columns], "rows": rows})
        return render_to_string("admin/imports/report.html", {
            "counts": [(label, obj.counts[key]) for key, label in COUNT_LABELS if obj.counts.get(key)],
            "sections": sections,
            "columns": report.get("columns", []),
            "unmapped": report.get("unmapped_headers", []),
            "missing": report.get("missing_headers", []),
            "catalog_created": report.get("catalog_created", []),
            "catalog_warnings": report.get("catalog_warnings", []),
            "variables_created": report.get("variables_created", []),
        })

    # Read-only: batches are written by the import.
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
