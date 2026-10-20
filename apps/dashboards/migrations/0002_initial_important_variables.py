"""The five important variables of docs/REQUISITOS.md §7.1, on a database that already has the
initial catalog (the one with the historical import). From then on they are edited in the admin.

Phenols only at 01, 08 and 10 (decided). The other four, along the main line of the plant: entry,
outlet of the primary separators, DNF, outlet of CL-4080, Fase I and the discharge.
"""

from django.db import migrations

MAIN_LINE = ["BA-4001", "BA-4005C", "BA-4005D", "DNF entrada", "CL-4080 salida", "BA-4009A", "BA-4008", "BA-4010"]

INITIAL = [
    ("Fenoles", ["BA-4001", "BA-4008", "BA-4010"]),
    ("Temperatura", MAIN_LINE),
    ("pH", MAIN_LINE),
    ("SST", MAIN_LINE),
    ("G&A", MAIN_LINE),
]


def create_important_variables(apps, schema_editor):
    Parameter = apps.get_model("catalog", "Parameter")
    SamplingPoint = apps.get_model("catalog", "SamplingPoint")
    ImportantVariable = apps.get_model("dashboards", "ImportantVariable")
    for order, (code, point_codes) in enumerate(INITIAL, start=1):
        parameter = Parameter.objects.filter(code__iexact=code).first()
        if parameter is None or ImportantVariable.objects.filter(parameter=parameter).exists():
            continue
        points = [point for point in (SamplingPoint.objects.filter(code__iexact=c).first() for c in point_codes) if point]
        if not points:
            continue
        item = ImportantVariable.objects.create(parameter=parameter, order=order)
        item.points.set(points)


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0001_initial"),
        ("dashboards", "0001_initial"),
    ]

    operations = [migrations.RunPython(create_important_variables, migrations.RunPython.noop)]
