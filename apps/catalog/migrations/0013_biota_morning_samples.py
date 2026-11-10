"""BIOTA samples at 7 a.m. and, when there is one, at 4 p.m. (decided on 2026-11-09,
docs/REQUISITOS.md §15).

- Its values known only by their day, or as "a. m.", go to 07:00 of the same day; those of "p. m."
  go to 16:00. The history of each value moves with it, so the cell at 07:00 shows the value and
  its history, and no one types a second value for a day that already has one.
- Its variables get the frequency «7 a. m.», except those still measured in the afternoon (a 4 p.m.
  value since September 2026: today pH, phenols and SST of BR-4081), which keep 7 a.m. and 4 p.m.

A value whose new time is already taken by another value of the same variable is left as it was.

The day and the morning start at 00:00 and the afternoon at 12:00 (Bogotá, without daylight saving
time), so the move is adding 7 or 4 hours, done in a few queries: production runs the migrations
when the container starts.
"""

import datetime

from django.db import migrations
from django.db.models import Exists, F, OuterRef, Q
from django.utils import timezone

# precision: (hour its taken_at has, hours to add)
MOVES = {"day": (0, 7), "am": (0, 7), "pm": (12, 4)}
AFTERNOON_SINCE = datetime.date(2026, 9, 1)


def to_morning(apps, schema_editor):
    Source = apps.get_model("catalog", "Source")
    Variable = apps.get_model("catalog", "Variable")
    Measurement = apps.get_model("measurements", "Measurement")
    MeasurementHistory = apps.get_model("measurements", "MeasurementHistory")

    biota = Source.objects.filter(code__iexact="BIOTA").first()
    if biota is None:
        return
    for precision, (hour, hours) in MOVES.items():
        delta = datetime.timedelta(hours=hours)
        values = Measurement.objects.filter(
            variable__source=biota, time_precision=precision, taken_at__hour=hour, taken_at__minute=0
        )
        clashes = values.filter(
            Exists(Measurement.objects.filter(variable=OuterRef("variable"), taken_at=OuterRef("taken_at") + delta))
        )
        kept = list(clashes.values_list("variable_id", "taken_at"))
        entries = MeasurementHistory.objects.filter(
            variable__source=biota, time_precision=precision, taken_at__hour=hour, taken_at__minute=0
        )
        for variable_id, taken_at in kept:
            entries = entries.exclude(Q(variable_id=variable_id) & Q(taken_at=taken_at))
        values.exclude(pk__in=clashes.values("pk")).update(taken_at=F("taken_at") + delta, time_precision="hour")
        entries.update(taken_at=F("taken_at") + delta, time_precision="hour")

    since = timezone.make_aware(datetime.datetime.combine(AFTERNOON_SINCE, datetime.time(0)))
    afternoon = Measurement.objects.filter(variable=OuterRef("pk"), taken_at__gte=since, taken_at__hour=16)
    variables = Variable.objects.filter(source=biota)
    variables.filter(Exists(afternoon)).update(time_resolution="twice_daily")
    variables.exclude(Exists(afternoon)).update(time_resolution="morning")


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0012_morning_frequency"),
        ("measurements", "0002_history_timestamp_index"),
    ]

    operations = [migrations.RunPython(to_morning, migrations.RunPython.noop)]
