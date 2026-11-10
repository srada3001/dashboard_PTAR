"""The Exportaciones page (docs/REQUISITOS.md §10): the weekly files, for the administrator only
(decided on 2026-11-09). The Explorador and ICAV keep their own Excel downloads for engineers."""

from django.http import StreamingHttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils.http import content_disposition_header

from apps.accounts.permissions import admin_required

from .models import WeeklyExport
from .storage import XLSX, storage

RECENT_WEEKS = 8


def weekly_context():
    weeks = list(WeeklyExport.objects.all()[:RECENT_WEEKS])
    return {"weeks": weeks, "preparing": any(week.status == WeeklyExport.Status.RUNNING for week in weeks)}


@admin_required
def index(request):
    return render(request, "exports/index.html", weekly_context())


@admin_required
def weekly_list(request):
    """The weekly files, refreshed by HTMX while one is being prepared."""
    return render(request, "exports/_weekly.html", weekly_context())


@admin_required
def weekly_download(request, pk):
    export = get_object_or_404(WeeklyExport, pk=pk, status=WeeklyExport.Status.DONE)
    # Streamed in chunks from the storage: the whole history is tens of megabytes.
    response = StreamingHttpResponse(storage().chunks(export.file_name), content_type=XLSX)
    response["Content-Disposition"] = content_disposition_header(True, export.file_name)
    return response
