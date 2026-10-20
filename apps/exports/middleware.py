import logging
import time

from django.conf import settings

from . import weekly

logger = logging.getLogger(__name__)


class WeeklyExportMiddleware:
    """Starts the week's export when it is due (apps/exports/weekly.py). Looks at most every few
    minutes per process, after the response, so requests do not wait for it."""

    INTERVAL = 300  # seconds

    def __init__(self, get_response):
        self.get_response = get_response
        self.next_look = 0.0

    def __call__(self, request):
        response = self.get_response(request)
        if settings.WEEKLY_EXPORT_AUTO and time.monotonic() >= self.next_look:
            self.next_look = time.monotonic() + self.INTERVAL
            try:
                weekly.ensure_current()
            except Exception:
                logger.exception("No se pudo revisar la exportación semanal")
        return response
