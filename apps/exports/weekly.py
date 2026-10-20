"""The weekly export (docs/REQUISITOS.md §10): each Monday, a file with all the data up to the Sunday
before, to be downloaded from the app and uploaded to SharePoint by hand.

There is no scheduler: the service runs a single instance whose database lives inside it, so a job
elsewhere could not read it. Instead, the first request after Monday 00:00 starts the file in the
background (WeeklyExportMiddleware); with the control room capturing every hour, that is minutes
after midnight. Two processes asking at once are fine: the week's row is created only once.
"""

import datetime
import logging
import os
import tempfile
import threading

from django.db import IntegrityError, connections, transaction
from django.utils import timezone

from . import workbook
from .models import WeeklyExport
from .storage import storage

logger = logging.getLogger(__name__)

# A file still "preparing" after this long died with its instance (a deploy, a restart): start again.
STALE = datetime.timedelta(minutes=30)
# A failed file is tried again after this long, not on every request.
RETRY = datetime.timedelta(hours=1)


def due_week(now=None):
    """The Monday of this week (Bogotá): from Monday 00:00 its file is due."""
    today = timezone.localdate(now)
    return today - datetime.timedelta(days=today.weekday())


def week_cut(week):
    """The file of a week has the measurements taken before its Monday at 00:00."""
    return timezone.make_aware(datetime.datetime.combine(week, datetime.time(0)))


def file_name(week):
    return f"datos_PTAR_hasta_{week - datetime.timedelta(days=1):%Y-%m-%d}.xlsx"


def claim(week, now=None):
    """The week's export if this caller must prepare it now, else None (it is ready, someone is
    preparing it, or it failed less than RETRY ago)."""
    now = now or timezone.now()
    with transaction.atomic():
        export = WeeklyExport.objects.filter(week=week).first()
        if export is None:
            try:
                with transaction.atomic():
                    return WeeklyExport.objects.create(week=week, status=WeeklyExport.Status.RUNNING, started_at=now)
            except IntegrityError:
                return None
        stale = export.status == WeeklyExport.Status.RUNNING and export.started_at < now - STALE
        retry = export.status == WeeklyExport.Status.FAILED and (export.finished_at or export.started_at) < now - RETRY
        if not (stale or retry):
            return None
        export.status, export.started_at, export.finished_at, export.error = WeeklyExport.Status.RUNNING, now, None, ""
        export.save()
        return export


def prepare(export):
    """Writes the week's workbook and keeps it in the storage. Never raises: a failure is kept in
    the row, to be shown and tried again later."""
    sunday = export.week - datetime.timedelta(days=1)
    readme = workbook.readme_lines(
        "Datos de calidad y operación de la PTAR (Dashboard PTAR).",
        f"Todas las mediciones hasta el domingo {sunday:%Y-%m-%d} inclusive.",
        [workbook.LONG, workbook.WIDE],
    )
    handle, path = tempfile.mkstemp(suffix=".xlsx")
    os.close(handle)
    try:
        count = workbook.write(path, readme, [workbook.LONG, workbook.WIDE], workbook.measurements(end=week_cut(export.week)))
        name = file_name(export.week)
        storage().save(name, path)
        export.status, export.file_name = WeeklyExport.Status.DONE, name
        export.size, export.measurements = os.path.getsize(path), count
    except Exception as error:  # noqa: BLE001 - any failure is reported in the page, not raised
        logger.exception("No se pudo preparar la exportación semanal %s", export.week)
        export.status, export.error = WeeklyExport.Status.FAILED, f"{type(error).__name__}: {error}"[:1000]
    finally:
        os.remove(path)
    export.finished_at = timezone.now()
    export.save()
    return export


def _prepare_in_background(pk):
    try:
        prepare(WeeklyExport.objects.get(pk=pk))
    finally:
        connections.close_all()


def ensure_current(now=None, background=True):
    """Starts this week's file if it is due and nobody has it; returns the export started, if any."""
    export = claim(due_week(now), now)
    if export is None:
        return None
    if background:
        threading.Thread(target=_prepare_in_background, args=(export.pk,), daemon=True, name="weekly-export").start()
    else:
        prepare(export)
    return export
