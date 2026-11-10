"""One flow per clarifier (decided on 2026-11-09, docs/REQUISITOS.md §15).

At a point that has both flows with data, the daily one of «Datos LABORATORIO» and PI's hourly one,
only the more complete (the one with more measurements) is kept. The other is repeated data, and
while the platform is being built it is deleted completely, as the user asked: its measurements,
its history and the variable itself. Once the platform is in use, the history is never deleted.
"""

from django.db import migrations, models

POINTS = ["BA-4005A", "BA-4005B", "BA-4005C", "BA-4005D", "Recirculación"]


def keep_most_complete(apps, schema_editor):
    Variable = apps.get_model("catalog", "Variable")
    CaptureFormVariable = apps.get_model("catalog", "CaptureFormVariable")
    WeeklyChartVariable = apps.get_model("dashboards", "WeeklyChartVariable")
    Measurement = apps.get_model("measurements", "Measurement")
    MeasurementHistory = apps.get_model("measurements", "MeasurementHistory")

    for code in POINTS:
        flows = list(Variable.objects.filter(point__code__iexact=code, parameter__code__iexact="Flujo"))
        counts = {variable.pk: Measurement.objects.filter(variable=variable).count() for variable in flows}
        if sum(1 for variable in flows if counts[variable.pk]) < 2:
            continue
        kept = max(flows, key=lambda variable: counts[variable.pk])
        for variable in flows:
            if variable.pk == kept.pk or not counts[variable.pk]:
                continue
            # The app's history refuses to be deleted; this one deletion is the user's decision.
            models.QuerySet.delete(MeasurementHistory.objects.filter(variable=variable))
            Measurement.objects.filter(variable=variable).delete()
            CaptureFormVariable.objects.filter(variable=variable).delete()
            WeeklyChartVariable.objects.filter(variable=variable).delete()
            variable.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0009_load_flows"),
        ("dashboards", "0004_initial_weekly_charts"),
        ("measurements", "0002_history_timestamp_index"),
    ]

    operations = [migrations.RunPython(keep_most_complete, migrations.RunPython.noop)]
