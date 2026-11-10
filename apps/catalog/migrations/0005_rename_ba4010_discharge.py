"""The Labviewer point «BA-4010 clarificada» (the «BA-4010 CLARIFICADA» block of «Datos
LABORATORIO») is now called «BA-4010 vertimiento». Its variables, measurements, limits and charts
keep pointing to it; the old name stays as an alias so the historical columns still find it."""

from django.db import migrations

OLD, NEW = "BA-4010 clarificada", "BA-4010 vertimiento"
DESCRIPTION = "Bloque «BA-4010 CLARIFICADA» de Labviewer"


def rename(apps, schema_editor):
    SamplingPoint = apps.get_model("catalog", "SamplingPoint")
    PointAlias = apps.get_model("catalog", "PointAlias")
    point = SamplingPoint.objects.filter(code__iexact=OLD).first()
    if point is None or SamplingPoint.objects.filter(code__iexact=NEW).exists():
        return
    point.code = NEW
    point.name = DESCRIPTION
    point.save(update_fields=["code", "name"])
    if not PointAlias.objects.filter(alias__iexact=OLD).exists():
        PointAlias.objects.create(point=point, alias=OLD)


class Migration(migrations.Migration):
    dependencies = [("catalog", "0004_initial_capture_forms")]

    operations = [migrations.RunPython(rename, migrations.RunPython.noop)]
