"""The cards of «Variables importantes» as decided on 2026-11-09 (docs/REQUISITOS.md §7.1): their
order, their titles and their series. From then on they are edited in the admin.

A card is found by its title, or by the name of the parameter it was before 0005; one that does not
exist is created. A series whose variable does not exist is left out.
"""

from django.db import migrations

LAB, ECOLAB, BIOTA = "Labviewer", "Ecolab", "BIOTA"
MAIN = ["BA-4001", "BA-4005C", "BA-4005D", "CL-4080 salida"]

# (title, former title, [(point, parameter, source)])
CARDS = [
    ("pH", "pH", [(point, "pH", ECOLAB) for point in MAIN]),
    ("Grasas y aceites", "Grasas y aceites", [
        ("BA-4001", "G&A", LAB), ("BA-4005C", "G&A", ECOLAB), ("BA-4005D", "G&A", ECOLAB),
        ("CL-4080 salida", "G&A", ECOLAB), ("BA-4010 vertimiento", "G&A", LAB),
    ]),
    ("Sólidos suspendidos totales", "Sólidos suspendidos totales", [
        ("BA-4001", "SST", ECOLAB), ("BA-4001", "SS", LAB), ("BA-4005C", "SST", ECOLAB),
        ("BA-4005D", "SST", ECOLAB), ("CL-4080 salida", "SST", ECOLAB), ("BA-4010 vertimiento", "SS", LAB),
    ]),
    ("Fenoles", "Fenoles", [
        ("BA-4001", "Fenoles", BIOTA), ("BA-4001", "Fenoles", LAB), ("BA-4008", "Fenoles", BIOTA),
        ("BA-4010", "Fenoles", BIOTA), ("BA-4010 vertimiento", "Fenoles", LAB),
    ]),
    ("DQO", "Demanda química de oxígeno", [
        ("BA-4001", "DQO", BIOTA), ("BA-4008", "DQO", BIOTA), ("BA-4010", "DQO", BIOTA),
    ]),
    ("Temperatura", "Temperatura", [(point, "Temperatura", ECOLAB) for point in MAIN]),
]


def configure(apps, schema_editor):
    Variable = apps.get_model("catalog", "Variable")
    ImportantVariable = apps.get_model("dashboards", "ImportantVariable")
    ImportantVariableItem = apps.get_model("dashboards", "ImportantVariableItem")

    def variable(point, parameter, source):
        return Variable.objects.filter(
            point__code__iexact=point, parameter__code__iexact=parameter, source__code__iexact=source
        ).first()

    for order, (title, former, keys) in enumerate(CARDS, start=1):
        variables = [found for found in (variable(*key) for key in keys) if found]
        if not variables:
            continue
        card = (
            ImportantVariable.objects.filter(title__iexact=title).first()
            or ImportantVariable.objects.filter(title__iexact=former).first()
            or ImportantVariable(title=title)
        )
        card.title, card.order = title, order
        card.save()
        card.items.all().delete()
        for position, found in enumerate(variables, start=1):
            ImportantVariableItem.objects.create(card=card, variable=found, order=position)


class Migration(migrations.Migration):
    dependencies = [("dashboards", "0005_important_variable_series")]

    operations = [migrations.RunPython(configure, migrations.RunPython.noop)]
