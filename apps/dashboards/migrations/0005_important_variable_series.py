"""Each card of «Variables importantes» becomes a title and a list of variables (decided on
2026-11-09, docs/REQUISITOS.md §7.1): a parameter at some points, with every source, could not drop
one source at one point nor put two parameters together (SST and SS).

The cards there are become the same list they showed: the variables of their parameter at their
points, every source, so nothing changes until they are edited.
"""

import django.db.models.deletion
from django.db import migrations, models


def to_series(apps, schema_editor):
    ImportantVariable = apps.get_model("dashboards", "ImportantVariable")
    ImportantVariableItem = apps.get_model("dashboards", "ImportantVariableItem")
    Variable = apps.get_model("catalog", "Variable")
    for card in ImportantVariable.objects.select_related("parameter"):
        card.title = card.parameter.name
        card.save(update_fields=["title"])
        points = list(card.points.order_by("area__order", "order", "code"))
        order = 0
        for point in points:
            for variable in Variable.objects.filter(parameter=card.parameter, point=point).order_by("source__code"):
                order += 1
                ImportantVariableItem.objects.create(card=card, variable=variable, order=order)


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0014_nalco_is_ecolab"),
        ("dashboards", "0004_initial_weekly_charts"),
    ]

    operations = [
        migrations.AddField(
            model_name="importantvariable",
            name="title",
            field=models.CharField(default="", max_length=120, verbose_name="título"),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name="ImportantVariableItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("order", models.PositiveSmallIntegerField(default=0, verbose_name="orden")),
                ("card", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="dashboards.importantvariable", verbose_name="tarjeta")),
                ("variable", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="+", to="catalog.variable", verbose_name="variable")),
            ],
            options={
                "verbose_name": "serie de la tarjeta",
                "verbose_name_plural": "series de la tarjeta",
                "ordering": ["order", "pk"],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("card", "variable"), name="importantvariableitem_unique",
                        violation_error_message="La variable ya está en la tarjeta.",
                    )
                ],
            },
        ),
        migrations.RunPython(to_series, migrations.RunPython.noop),
        migrations.RemoveField(model_name="importantvariable", name="points"),
        migrations.RemoveField(model_name="importantvariable", name="parameter"),
        migrations.AlterField(
            model_name="importantvariable",
            name="title",
            field=models.CharField(help_text="Por ejemplo, «Sólidos suspendidos totales».", max_length=120, unique=True, verbose_name="título"),
        ),
    ]
