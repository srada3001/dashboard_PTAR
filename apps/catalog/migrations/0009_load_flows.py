"""The clarifiers and the load flows (decided on 2026-11-09, docs/REQUISITOS.md §15).

- «Clarificador A» to «Clarificador D» of «Datos LABORATORIO» are BA-4005A to BA-4005D. A and B are
  renamed; C and D join the points BA-4005C and BA-4005D that already existed (Ecolab's analyses and
  PI's flow), with their variables, measurements and limits. The old names stay as aliases.
- The form «Flujos de PI» becomes «Flujos de carga», hourly: the PI flows of BA-4005A to BA-4005D
  and of the recirculation, created when missing. It replaces «Flujos y niveles del laboratorio»,
  the daily form of the same flows; whoever had that one gets «Flujos de carga». The daily values
  of the history keep their variables and their source.

Nothing happens on a database without those points and forms.
"""

from django.db import migrations

CLARIFIERS = "ABCD"
# Order of the points of the primary treatment: each clarifier next to the joint outlet of its pair.
POINT_ORDER = ["BA-4005A/B", "BA-4005A", "BA-4005B", "BA-4005C/D", "BA-4005C", "BA-4005D"]
FORM_POINTS = ["BA-4005A", "BA-4005B", "BA-4005C", "BA-4005D", "Recirculación"]


def merge_points(apps):
    SamplingPoint = apps.get_model("catalog", "SamplingPoint")
    PointAlias = apps.get_model("catalog", "PointAlias")
    Variable = apps.get_model("catalog", "Variable")
    Limit = apps.get_model("catalog", "Limit")
    ImportantVariable = apps.get_model("dashboards", "ImportantVariable")

    for letter in CLARIFIERS:
        old_name, code = f"Clarificador {letter}", f"BA-4005{letter}"
        old = SamplingPoint.objects.filter(code__iexact=old_name).first()
        if old is None:
            continue
        target = SamplingPoint.objects.filter(code__iexact=code).first()
        if target is None:
            old.code, old.name = code, old.name or old_name
            old.save(update_fields=["code", "name"])
            target = old
        else:
            clashes = [
                v for v in old.variables.all()
                if Variable.objects.filter(point=target, parameter=v.parameter_id, source=v.source_id).exists()
            ]
            if clashes:
                continue  # the same variable at both: a person decides
            old.variables.update(point=target)
            Limit.objects.filter(point=old).update(point=target)
            PointAlias.objects.filter(point=old).update(point=target)
            # The cards chose points until dashboards/0005; since then they choose variables, which
            # already moved with the point.
            if any(f.name == "points" for f in ImportantVariable._meta.get_fields()):
                for important in ImportantVariable.objects.filter(points=old):
                    important.points.remove(old)
                    important.points.add(target)
            if not target.name:
                target.name = old_name
                target.save(update_fields=["name"])
            old.delete()
        if not PointAlias.objects.filter(alias__iexact=old_name).exists():
            PointAlias.objects.create(point=target, alias=old_name)

    for order, code in enumerate(POINT_ORDER, start=2):
        SamplingPoint.objects.filter(code__iexact=code).update(order=order)


def load_flows_form(apps):
    Source = apps.get_model("catalog", "Source")
    SamplingPoint = apps.get_model("catalog", "SamplingPoint")
    Parameter = apps.get_model("catalog", "Parameter")
    Variable = apps.get_model("catalog", "Variable")
    CaptureForm = apps.get_model("catalog", "CaptureForm")
    CaptureFormVariable = apps.get_model("catalog", "CaptureFormVariable")
    User = apps.get_model("accounts", "User")

    pi = Source.objects.filter(code__iexact="PI").first()
    flow = Parameter.objects.filter(code__iexact="Flujo").first()
    form = CaptureForm.objects.filter(name__iexact="Flujos de PI", source=pi).first() if pi else None
    if form is None or flow is None:
        return
    form.name, form.schedule = "Flujos de carga", "hourly"
    form.save(update_fields=["name", "schedule"])
    order = 0
    for code in FORM_POINTS:
        point = SamplingPoint.objects.filter(code__iexact=code).first()
        if point is None:
            continue
        variable, _ = Variable.objects.get_or_create(
            point=point, parameter=flow, source=pi, defaults={"time_resolution": "hourly"}
        )
        order += 1
        CaptureFormVariable.objects.update_or_create(form=form, variable=variable, defaults={"order": order})

    daily = CaptureForm.objects.filter(name__iexact="Flujos y niveles del laboratorio").first()
    if daily is not None:
        for user in User.objects.filter(capture_forms=daily):
            user.capture_forms.add(form)
        daily.delete()


def apply(apps, schema_editor):
    merge_points(apps)
    load_flows_form(apps)


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0008_ecodiesel_to_biota"),
        ("dashboards", "0004_initial_weekly_charts"),
        ("accounts", "0001_initial"),
    ]

    operations = [migrations.RunPython(apply, migrations.RunPython.noop)]
