"""Ecodiesel is measured by BIOTA too (decided on 2026-11-09, docs/REQUISITOS.md §15).

Its variables go from the provisional source «Por confirmar» to BIOTA, with their measurements, and
become the «Ecodiesel» section of the «BIOTA» form, below «DIAPAC». The «Ecodiesel» form goes away;
whoever had it gets «BIOTA». Nothing happens on a database without those forms.
"""

from django.db import migrations

POINT, FORM, SECTION = "Ecodiesel", "BIOTA", "Ecodiesel"


def move_ecodiesel(apps, schema_editor):
    Source = apps.get_model("catalog", "Source")
    SamplingPoint = apps.get_model("catalog", "SamplingPoint")
    Variable = apps.get_model("catalog", "Variable")
    CaptureForm = apps.get_model("catalog", "CaptureForm")
    CaptureFormVariable = apps.get_model("catalog", "CaptureFormVariable")
    User = apps.get_model("accounts", "User")

    biota = Source.objects.filter(code__iexact="BIOTA").first()
    pending = Source.objects.filter(code__iexact="Por confirmar").first()
    point = SamplingPoint.objects.filter(code__iexact=POINT).first()
    if biota is None:
        return
    if pending is not None and point is not None:
        for variable in Variable.objects.filter(point=point, source=pending):
            # Never merge two variables: if BIOTA already has this one, it stays for a person to decide.
            if not Variable.objects.filter(point=point, parameter=variable.parameter_id, source=biota).exists():
                variable.source = biota
                variable.save(update_fields=["source"])

    form = CaptureForm.objects.filter(name__iexact=FORM, source=biota).first()
    ecodiesel = CaptureForm.objects.filter(name__iexact="Ecodiesel").first()
    if form is None or ecodiesel is None:
        return
    items = list(ecodiesel.items.select_related("variable").order_by("order", "pk"))
    if any(item.variable.source_id != biota.pk for item in items):
        return  # some variable is not BIOTA's: the form stays for a person to decide
    order = max(form.items.values_list("order", flat=True), default=0)
    for item in items:
        order += 1
        CaptureFormVariable.objects.get_or_create(
            form=form, variable=item.variable, defaults={"order": order, "section": SECTION}
        )
    for user in User.objects.filter(capture_forms=ecodiesel):
        user.capture_forms.add(form)
    ecodiesel.delete()


class Migration(migrations.Migration):
    dependencies = [("catalog", "0007_diapac_to_biota")]

    operations = [migrations.RunPython(move_ecodiesel, migrations.RunPython.noop)]
