"""Nalco is now called Ecolab (decided on 2026-11-09, docs/REQUISITOS.md §15).

The source and its capture form are renamed; their variables, measurements, limits and charts keep
pointing to them. The import still reads the Nalco workbook: its map says «Nalco», and the import
takes it as Ecolab (apps/imports/catalog.py) until the Excel import is removed.
"""

from django.db import migrations, models


def rename(apps, schema_editor):
    Source = apps.get_model("catalog", "Source")
    CaptureForm = apps.get_model("catalog", "CaptureForm")
    if not Source.objects.filter(code__iexact="Ecolab").exists():
        Source.objects.filter(code__iexact="Nalco").update(code="Ecolab")
    if not CaptureForm.objects.filter(name__iexact="Ecolab").exists():
        CaptureForm.objects.filter(name__iexact="Nalco").update(name="Ecolab")


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0013_biota_morning_samples'),
    ]

    operations = [
        migrations.AlterField(
            model_name='source',
            name='code',
            field=models.CharField(help_text='Nombre corto: Labviewer, BIOTA, Ecolab, PI.', max_length=30, verbose_name='código'),
        ),
        migrations.RunPython(rename, migrations.RunPython.noop),
    ]
