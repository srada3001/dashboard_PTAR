"""Variables sampled in the morning and the afternoon («A.AGRIAS SEP.») were imported as "7 a. m. y
4 p. m."; their measurements say a. m. or p. m., so their frequency is "a. m. y p. m."."""

from django.db import migrations


def mark_am_pm(apps, schema_editor):
    Variable = apps.get_model("catalog", "Variable")
    Measurement = apps.get_model("measurements", "Measurement")
    sampled = Measurement.objects.filter(time_precision__in=["am", "pm"]).values("variable_id")
    Variable.objects.filter(pk__in=sampled, time_resolution="twice_daily").update(time_resolution="am_pm")


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0002_am_pm_frequency"),
        ("measurements", "0002_history_timestamp_index"),
    ]

    operations = [migrations.RunPython(mark_am_pm, migrations.RunPython.noop)]
