"""DIAPAC is measured by BIOTA (decided on 2026-11-09, docs/REQUISITOS.md §15).

- The variables of the «DIAPAC» sheet (afluente, cámara A and cámara B) go from the provisional
  source «Por confirmar» to BIOTA, with their measurements. «DIAPAC efluente» is measured by
  Labviewer and stays as it is.
- The form «BIOTA Fase I» is renamed «BIOTA» and gets two sections: «Fase I», what it already had,
  and below it «DIAPAC», with the variables of each point together (the five of each chamber, not
  Sunday's and Tuesday's apart). The «DIAPAC» form goes away; whoever had it gets «BIOTA».

Nothing happens on a database without those forms (a new one, before the historical import).
"""

from django.db import migrations

POINTS = ["DIAPAC afluente", "DIAPAC cámara A", "DIAPAC cámara B"]
OLD_NAME, NEW_NAME, OLD_SECTION, NEW_SECTION = "BIOTA Fase I", "BIOTA", "Fase I", "DIAPAC"


def grouped_by_point(items):
    """The items with those of each point together, points in the order they first appear."""
    first = {}
    for index, item in enumerate(items):
        first.setdefault(item.variable.point_id, index)
    return sorted(items, key=lambda item: first[item.variable.point_id])


def move_diapac(apps, schema_editor):
    Source = apps.get_model("catalog", "Source")
    SamplingPoint = apps.get_model("catalog", "SamplingPoint")
    Variable = apps.get_model("catalog", "Variable")
    CaptureForm = apps.get_model("catalog", "CaptureForm")
    CaptureFormVariable = apps.get_model("catalog", "CaptureFormVariable")
    User = apps.get_model("accounts", "User")

    biota = Source.objects.filter(code__iexact="BIOTA").first()
    pending = Source.objects.filter(code__iexact="Por confirmar").first()
    if biota is None:
        return
    points = [point for code in POINTS if (point := SamplingPoint.objects.filter(code__iexact=code).first())]
    if pending is not None:
        for variable in Variable.objects.filter(point__in=points, source=pending):
            # Never merge two variables: if BIOTA already has this one, it stays for a person to decide.
            if not Variable.objects.filter(point=variable.point_id, parameter=variable.parameter_id, source=biota).exists():
                variable.source = biota
                variable.save(update_fields=["source"])

    form = CaptureForm.objects.filter(name__iexact=OLD_NAME, source=biota).first()
    if form is None:
        return
    if not CaptureForm.objects.filter(name__iexact=NEW_NAME).exists():
        form.name = NEW_NAME
        form.save(update_fields=["name"])
    form.items.filter(section="").update(section=OLD_SECTION)

    diapac = CaptureForm.objects.filter(name__iexact="DIAPAC").first()
    if diapac is None:
        return
    items = list(diapac.items.select_related("variable").order_by("order", "pk"))
    if any(item.variable.source_id != biota.pk for item in items):
        return  # some variable is not BIOTA's: the form stays for a person to decide
    order = max(form.items.values_list("order", flat=True), default=0)
    for item in grouped_by_point(items):
        order += 1
        CaptureFormVariable.objects.get_or_create(
            form=form, variable=item.variable, defaults={"order": order, "section": NEW_SECTION}
        )
    for user in User.objects.filter(capture_forms=diapac):
        user.capture_forms.add(form)
    diapac.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0006_capture_form_sections"),
        ("accounts", "0001_initial"),
    ]

    operations = [migrations.RunPython(move_diapac, migrations.RunPython.noop)]
