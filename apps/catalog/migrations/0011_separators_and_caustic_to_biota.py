"""The separators and sour water («A.AGRIAS SEP.») and the spent caustic («K-SODAS») are measured
by BIOTA too (decided on 2026-11-09, docs/REQUISITOS.md §15).

Their variables go from the provisional source «Por confirmar» to BIOTA, with their measurements,
and become two more sections of the «BIOTA» form, below «Ecodiesel»: «Aguas agrias a los
separadores» and «Sodas gastadas». Their two forms go away; whoever had them gets «BIOTA».
Nothing happens on a database without those forms.
"""

from django.db import migrations

POINTS = [
    "Agua agria", "SE-3010", "SE-3020", "SE-3030", "SE-3050", "SE-3060",
    "K-4090", "K-4091", "K-4092", "K-4094", "D-4006",
]
# (form that goes away, section of «BIOTA» it becomes)
FORMS = [
    ("Separadores y agua agria", "Aguas agrias a los separadores"),
    ("Sodas gastadas", "Sodas gastadas"),
]


def move_to_biota(apps, schema_editor):
    Source = apps.get_model("catalog", "Source")
    Variable = apps.get_model("catalog", "Variable")
    CaptureForm = apps.get_model("catalog", "CaptureForm")
    CaptureFormVariable = apps.get_model("catalog", "CaptureFormVariable")
    User = apps.get_model("accounts", "User")

    biota = Source.objects.filter(code__iexact="BIOTA").first()
    pending = Source.objects.filter(code__iexact="Por confirmar").first()
    if biota is None:
        return
    if pending is not None:
        for code in POINTS:
            for variable in Variable.objects.filter(point__code__iexact=code, source=pending):
                # Never merge two variables: if BIOTA already has this one, it stays for a person to decide.
                if not Variable.objects.filter(point=variable.point_id, parameter=variable.parameter_id, source=biota).exists():
                    variable.source = biota
                    variable.save(update_fields=["source"])

    form = CaptureForm.objects.filter(name__iexact="BIOTA", source=biota).first()
    if form is None:
        return
    for name, section in FORMS:
        old = CaptureForm.objects.filter(name__iexact=name).first()
        if old is None:
            continue
        items = list(old.items.select_related("variable").order_by("order", "pk"))
        if any(item.variable.source_id != biota.pk for item in items):
            continue  # some variable is not BIOTA's: the form stays for a person to decide
        order = max(form.items.values_list("order", flat=True), default=0)
        for item in items:
            order += 1
            CaptureFormVariable.objects.get_or_create(
                form=form, variable=item.variable, defaults={"order": order, "section": section}
            )
        for user in User.objects.filter(capture_forms=old):
            user.capture_forms.add(form)
        old.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0010_one_flow_per_clarifier"),
        ("accounts", "0001_initial"),
    ]

    operations = [migrations.RunPython(move_to_biota, migrations.RunPython.noop)]
