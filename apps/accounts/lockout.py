"""Read and clear django-axes lockouts for a given username (used by the admin)."""

from axes.models import AccessAttempt
from axes.utils import reset
from django.conf import settings
from django.db.models import Sum
from django.utils import timezone


def is_locked(username: str) -> bool:
    """Mirror of axes' own check: failures for this username inside the cool-off window."""
    window_start = timezone.now() - settings.AXES_COOLOFF_TIME
    failures = AccessAttempt.objects.filter(
        username=username, attempt_time__gte=window_start
    ).aggregate(total=Sum("failures_since_start"))["total"]
    return (failures or 0) >= settings.AXES_FAILURE_LIMIT


def unlock(username: str) -> None:
    reset(username=username)
