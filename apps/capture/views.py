import datetime

from django.db import transaction
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.accounts.permissions import capture_required
from apps.catalog.models import Variable
from apps.measurements import records
from apps.measurements.models import Measurement, MeasurementHistory
from apps.measurements.values import InvalidValue, format_number, outside_physical_range, outside_typical_range, parse_value

from .grid import SLOTS, build, display, may_change, note, slots_of


def range_text(low, high, unit=""):
    if low is None and high is None:
        return ""
    unit = f" {unit}" if unit else ""
    if low is None:
        return f"hasta {format_number(high)}{unit}"
    if high is None:
        return f"desde {format_number(low)}{unit}"
    return f"{format_number(low)} a {format_number(high)}{unit}"


def capture_form(request, pk):
    """A form of this person's scope; any other is not found, whatever the URL says."""
    return get_object_or_404(request.user.allowed_capture_forms().select_related("source"), pk=pk)


def chosen_day(text):
    """The day asked for, never after today."""
    today = timezone.localdate()
    try:
        day = datetime.date.fromisoformat(text or "")
    except ValueError:
        return today
    return min(day, today)


@capture_required
def index(request):
    """The capture forms this person may fill."""
    forms = request.user.allowed_capture_forms().select_related("source").prefetch_related("items")
    return render(request, "capture/index.html", {"capture_forms": forms})


@capture_required
def grid(request, pk):
    form = capture_form(request, pk)
    day = chosen_day(request.GET.get("date"))
    grid = build(form, day, request.user)
    variables = {
        variable.pk: {
            "label": f"{variable.point} · {variable.parameter} · {variable.source}",
            "unit": variable.parameter.unit,
            "physical": range_text(variable.parameter.physical_min, variable.parameter.physical_max, variable.parameter.unit),
            "typical": range_text(variable.typical_min, variable.typical_max, variable.parameter.unit),
        }
        for variable in grid.variables
    }
    today = timezone.localdate()
    return render(request, "capture/grid.html", {
        "form": form,
        "grid": grid,
        "variables": variables,
        "today": today,
        "previous_day": day - datetime.timedelta(days=1),
        "next_day": day + datetime.timedelta(days=1) if day < today else None,
    })


class Answer:
    """What the grid's script receives about a cell after trying to save it."""

    @staticmethod
    def cell(state, measurement, user, now, message=""):
        return JsonResponse({
            "state": state,
            "message": message,
            "value": display(measurement),
            "version": records.version(measurement),
            "note": " ".join(part for part in (note(measurement), may_change(user, measurement, now)[1]) if part),
            "readonly": not may_change(user, measurement, now)[0],
            "suspect": bool(measurement and measurement.suspect),
        })

    @staticmethod
    def refuse(state, message, status=200):
        return JsonResponse({"state": state, "message": message}, status=status)

    @staticmethod
    def confirm(message, reason):
        return JsonResponse({"state": "confirm", "message": message, "reason": reason})


def cell_of(form, data):
    """(variable, slot, taken_at) of the cell a request names, or 404 if it is not in the form."""
    try:
        variable = form.variables.select_related("point", "parameter", "source").get(pk=int(data.get("variable", "")))
    except (ValueError, Variable.DoesNotExist):
        raise Http404 from None
    slot = SLOTS.get(data.get("slot", ""))
    if slot not in slots_of(variable):
        raise Http404
    try:
        day = datetime.date.fromisoformat(data.get("date", ""))
    except ValueError:
        raise Http404 from None
    return variable, slot, slot.taken_at(day)


@capture_required
@require_POST
def save_cell(request, pk):
    """Saves, corrects or deletes the value of one cell. The server decides: a number with an
    optional "<" or ">", inside the parameter's physical range; outside the variable's usual range,
    or replacing or deleting a value, it asks to confirm first (with an optional reason)."""
    form = capture_form(request, pk)
    variable, slot, taken_at = cell_of(form, request.POST)
    user, now = request.user, timezone.now()
    if taken_at > now:
        return Answer.refuse("refused", "No se capturan datos de horas o fechas futuras.")
    text = request.POST.get("value", "").strip()
    confirmed = request.POST.get("confirm") == "1"
    reason = request.POST.get("reason", "").strip()

    with transaction.atomic():
        current = (
            Measurement.objects.select_related("created_by", "updated_by")
            .filter(variable=variable, taken_at=taken_at).first()
        )
        if records.version(current) != request.POST.get("original", ""):
            message = f"Otra persona cambió esta celda mientras tanto; ahora es «{display(current) or 'vacía'}»."
            return Answer.cell("conflict", current, user, now, message)

        if not text:
            if current is None:
                return Answer.cell("unchanged", None, user, now)
            allowed, why = may_change(user, current, now)
            if not allowed:
                return Answer.refuse("refused", why)
            if not confirmed:
                return Answer.confirm(f"¿Borrar «{display(current)}»?", reason=True)
            records.delete(current, user, reason=reason)
            return Answer.cell("deleted", None, user, now)

        try:
            parsed = parse_value(text)
        except InvalidValue as error:
            return Answer.refuse("invalid", str(error))
        parameter = variable.parameter
        if outside_physical_range(parameter, parsed.value):
            limits = range_text(parameter.physical_min, parameter.physical_max, parameter.unit)
            return Answer.refuse("invalid", f"Imposible para {parameter}: el rango físico es {limits}.")
        typed = f"{parsed.qualifier}{format_number(parsed.value)}"
        if current is not None and not current.suspect and (current.value, current.qualifier) == (parsed.value, parsed.qualifier):
            return Answer.cell("unchanged", current, user, now)
        if current is not None:
            allowed, why = may_change(user, current, now)
            if not allowed:
                return Answer.refuse("refused", why)

        questions = []
        if outside_typical_range(variable, parsed.value):
            usual = range_text(variable.typical_min, variable.typical_max, parameter.unit)
            questions.append(f"{typed} en {variable.point} está fuera del rango habitual ({usual}).")
        if current is not None:
            questions.append(f"Corrige «{display(current)}» por «{typed}».")
        if questions and not confirmed:
            return Answer.confirm(" ".join(questions) + " ¿Guardar?", reason=current is not None)

        measurement = records.write(variable, taken_at, slot.precision, parsed, user, reason=reason)
    measurement = Measurement.objects.select_related("created_by", "updated_by").get(pk=measurement.pk)
    return Answer.cell("saved", measurement, user, now)


@capture_required
def cell_history(request, pk):
    """Every creation, correction and deletion of one cell, newest first."""
    form = capture_form(request, pk)
    variable, slot, taken_at = cell_of(form, request.GET)
    entries = (
        MeasurementHistory.objects.filter(variable=variable, taken_at=taken_at)
        .select_related("user", "batch").defer("batch__report", "batch__counts")
    )
    return render(request, "capture/_history.html", {"variable": variable, "slot": slot, "taken_at": taken_at, "entries": entries})

