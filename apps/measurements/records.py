"""Creating, correcting and deleting a measurement, always with its history (docs/REQUISITOS.md §5–§6).

Who may do it is decided by the caller (the capture checks scopes and the 24-hour rule); here every
change leaves a MeasurementHistory row with the value before and after, who, when and the reason.
"""

from django.db import transaction

from .models import Measurement, MeasurementHistory, Origin


def version(measurement):
    """What a client saw of a measurement, to notice that someone else changed it since:
    '' when there was none."""
    if measurement is None:
        return ""
    return f"{measurement.pk}.{measurement.updated_at.timestamp():.6f}"


def history(measurement, action, user, reason, old=None):
    return MeasurementHistory.objects.create(
        measurement=measurement,
        variable_id=measurement.variable_id,
        taken_at=measurement.taken_at,
        time_precision=measurement.time_precision,
        action=action,
        old_value=old.value if old else None,
        old_qualifier=old.qualifier if old else "",
        new_value=None if action == MeasurementHistory.Action.DELETE else measurement.value,
        new_qualifier="" if action == MeasurementHistory.Action.DELETE else measurement.qualifier,
        new_suspect=False if action == MeasurementHistory.Action.DELETE else measurement.suspect,
        user=user,
        reason=reason[:300],
    )


@transaction.atomic
def write(variable, taken_at, precision, parsed, user, *, reason="", origin=Origin.MANUAL):
    """Creates the measurement of a variable at a time, or corrects the one there is. A corrected
    value passed the validation, so it is no longer suspect. Returns the measurement."""
    measurement = Measurement.objects.filter(variable=variable, taken_at=taken_at).first()
    if measurement is None:
        measurement = Measurement.objects.create(
            variable=variable, taken_at=taken_at, time_precision=precision, value=parsed.value,
            qualifier=parsed.qualifier, origin=origin, created_by=user,
        )
        history(measurement, MeasurementHistory.Action.CREATE, user, reason)
        return measurement
    old = Measurement(value=measurement.value, qualifier=measurement.qualifier)
    measurement.value, measurement.qualifier = parsed.value, parsed.qualifier
    measurement.time_precision = precision
    measurement.suspect = False
    measurement.updated_by = user
    measurement.save()
    history(measurement, MeasurementHistory.Action.UPDATE, user, reason, old=old)
    return measurement


@transaction.atomic
def delete(measurement, user, *, reason=""):
    """Deletes a measurement. Its history stays, with this deletion as its last entry."""
    history(measurement, MeasurementHistory.Action.DELETE, user, reason, old=measurement)
    measurement.delete()
