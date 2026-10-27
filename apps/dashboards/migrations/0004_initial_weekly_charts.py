"""The ICAV charts of docs/REQUISITOS.md §7.3, the ones of the «Graficas» sheet of reference table
2, on a database that already has the initial catalog (the one with the historical import). From
then on they are edited in the admin.

The Labviewer columns of those pivot tables are the ones of the «BA-4010 CLARIFICADA» block. A
variable that does not exist is left out; a chart with none is not created.
"""

from django.db import migrations

LAB, BIOTA, UNKNOWN = "Labviewer", "BIOTA", "Por confirmar"

INITIAL = [
    ("Grasas y aceites", [
        ("BA-4001", "G&A", LAB), ("BA-4055", "G&A", LAB), ("BA-4010 clarificada", "G&A", LAB), ("BA-4010", "G&A", BIOTA),
    ]),
    ("Fenoles", [
        ("BA-4001", "Fenoles", BIOTA), ("BA-4009A", "Fenoles", BIOTA), ("BA-4008", "Fenoles", BIOTA),
        ("BA-4010", "Fenoles", BIOTA), ("BA-4010 clarificada", "Fenoles", LAB),
    ]),
    ("Sólidos suspendidos", [
        ("BA-4001", "SS", LAB), ("BA-4055", "SS", LAB), ("BA-4010 clarificada", "SS", LAB), ("BA-4010", "SST", BIOTA),
    ]),
    ("Biorreactor BA-4008 (aguas agrias)", [
        ("BA-4008 salida", "N total", BIOTA), ("BA-4008 salida", "N-NH3", BIOTA),
    ]),
    ("Nitrógeno", [
        ("BA-4008 entrada", "N total", BIOTA), ("BA-4008 salida", "N total", BIOTA), ("BA-4009A entrada", "N total", BIOTA),
        ("BA-4010", "N total", BIOTA), ("BA-4008 salida", "N-NH3", BIOTA), ("BA-4010", "N-NH3", BIOTA),
        ("BA-4010 clarificada", "N total", LAB),
    ]),
    ("Sulfatos de los separadores", [
        (point, "Sulfatos", UNKNOWN) for point in ("SE-3010", "SE-3020", "SE-3030", "SE-3050", "SE-3060")
    ]),
    ("Sulfatos de la PTAR", [
        ("BA-4009A entrada", "Sulfatos", BIOTA), ("BA-4008", "Sulfatos", BIOTA), ("BA-4009A", "Sulfatos", BIOTA),
        ("BA-4010", "Sulfatos", BIOTA), ("BA-4010 clarificada", "Sulfatos", LAB),
    ]),
    ("Fenoles en agua agria", [
        ("Agua agria", "Fenoles", UNKNOWN),
    ]),
]


def create_weekly_charts(apps, schema_editor):
    Variable = apps.get_model("catalog", "Variable")
    WeeklyChart = apps.get_model("dashboards", "WeeklyChart")
    WeeklyChartVariable = apps.get_model("dashboards", "WeeklyChartVariable")
    for order, (title, keys) in enumerate(INITIAL, start=1):
        if WeeklyChart.objects.filter(title=title).exists():
            continue
        variables = [
            variable
            for variable in (
                Variable.objects.filter(
                    point__code__iexact=point, parameter__code__iexact=parameter, source__code__iexact=source
                ).first()
                for point, parameter, source in keys
            )
            if variable
        ]
        if not variables:
            continue
        chart = WeeklyChart.objects.create(title=title, order=order)
        for position, variable in enumerate(variables, start=1):
            WeeklyChartVariable.objects.create(chart=chart, variable=variable, order=position)


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0001_initial"),
        ("dashboards", "0003_weekly_charts"),
    ]

    operations = [migrations.RunPython(create_weekly_charts, migrations.RunPython.noop)]
