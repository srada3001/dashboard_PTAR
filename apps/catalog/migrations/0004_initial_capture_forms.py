"""The initial capture forms of docs/REQUISITOS.md §6, one per sheet of today's Excel, with the
variables of its import map (import_maps/) in the order of its columns.

Only variables with data since October 2025 go in (decided on 2026-10-20): the rest stay in the
database and the views, and the administrator adds them to a form if they are measured again.
What exists is never removed: a form that already exists gets the missing variables, and those of
the map take the map's order. From then on the forms are edited in the admin.
"""

import csv
import datetime

from django.conf import settings
from django.db import migrations
from django.utils import timezone

SINCE = datetime.date(2025, 10, 1)

# (name, source, form shape, import maps whose columns of that source it takes)
FORMS = [
    ("Nalco", "Nalco", "hourly", ["Tabla1"]),
    ("Flujos de PI", "PI", "hourly", ["Tabla1"]),
    ("BIOTA Fase I", "BIOTA", "twice_daily", ["FASE1", "BR_4081"]),
    ("Laboratorio central", "Labviewer", "daily", ["Laboratorio"]),
    ("Flujos y niveles del laboratorio", "Por confirmar", "daily", ["Laboratorio"]),
    ("Separadores y agua agria", "Por confirmar", "am_pm", ["FenolAASepSoda4"]),
    ("Sodas gastadas", "Por confirmar", "occasional", ["FenolAASepSoda48"]),
    ("DIAPAC", "Por confirmar", "occasional", ["DIAPAC"]),
    ("Ecodiesel", "Por confirmar", "occasional", ["Ecodisel"]),
]


def map_columns(table):
    path = settings.BASE_DIR / "import_maps" / f"{table}.csv"
    if not path.exists():
        return []
    with open(path, encoding="utf-8", newline="") as file:
        return [row for row in csv.DictReader(file) if row["action"] == "import"]


def create_forms(apps, schema_editor):
    Source = apps.get_model("catalog", "Source")
    SamplingPoint = apps.get_model("catalog", "SamplingPoint")
    PointAlias = apps.get_model("catalog", "PointAlias")
    Parameter = apps.get_model("catalog", "Parameter")
    Variable = apps.get_model("catalog", "Variable")
    CaptureForm = apps.get_model("catalog", "CaptureForm")
    CaptureFormVariable = apps.get_model("catalog", "CaptureFormVariable")
    Measurement = apps.get_model("measurements", "Measurement")
    since = timezone.make_aware(datetime.datetime.combine(SINCE, datetime.time(0)))

    def point(code):
        found = SamplingPoint.objects.filter(code__iexact=code).first()
        if found is None:
            alias = PointAlias.objects.filter(alias__iexact=code).select_related("point").first()
            found = alias.point if alias else None
        return found

    for name, source_code, schedule, tables in FORMS:
        source = Source.objects.filter(code__iexact=source_code).first()
        if source is None:
            continue
        variables = []
        for table in tables:
            for column in map_columns(table):
                if column["source"].lower() != source_code.lower():
                    continue
                variable = Variable.objects.filter(
                    point=point(column["point"]),
                    parameter=Parameter.objects.filter(code__iexact=column["parameter"]).first(),
                    source=source,
                ).first()
                if variable is not None and variable not in variables:
                    variables.append(variable)
        variables = [v for v in variables if Measurement.objects.filter(variable=v, taken_at__gte=since).exists()]
        if not variables:
            continue
        form = CaptureForm.objects.filter(name__iexact=name).first()
        if form is None:
            form = CaptureForm.objects.create(name=name, source=source, schedule=schedule)
        elif form.source_id != source.pk:
            continue
        for order, variable in enumerate(variables, start=1):
            item, created = CaptureFormVariable.objects.get_or_create(form=form, variable=variable, defaults={"order": order})
            if not created and item.order != order:
                item.order = order
                item.save(update_fields=["order"])


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0003_am_pm_variables"),
        ("measurements", "0002_history_timestamp_index"),
    ]

    operations = [migrations.RunPython(create_forms, migrations.RunPython.noop)]
