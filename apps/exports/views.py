"""The Exportaciones page (docs/REQUISITOS.md §10), for the administrator and the engineers
(decided on 2026-11-11): the data of some laboratories (sources) and dates, at once, for both;
and the weekly file with the whole history, for the administrator only, showing just the one of
the Sunday before."""

import datetime
import io

from django import forms
from django.http import FileResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.http import content_disposition_header

from apps.accounts.permissions import admin_required, reader_required
from apps.catalog.models import Source
from apps.dashboards.stats import day_span

from . import workbook
from .models import WeeklyExport
from .storage import XLSX, storage
from .templatetags.exports import thousands

# What can be downloaded at once: Firebase cuts requests longer than 60 seconds.
MAX_AT_ONCE = 100_000
SHAPES = [(workbook.LONG, "Larga: una fila por medición"), (workbook.WIDE, "Ancha: una hoja por fuente, como las hojas de hoy")]


class SourceChoice(forms.ModelMultipleChoiceField):
    def label_from_instance(self, source):
        return f"{source.code} ({source.name})" if source.name and source.name != source.code else source.code


class ExportForm(forms.Form):
    start = forms.DateField(label="Desde", widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"))
    end = forms.DateField(label="Hasta", widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"))
    sources = SourceChoice(
        Source.objects.all(), label="Laboratorios", required=False, widget=forms.CheckboxSelectMultiple,
        help_text="Ninguno marcado: todos.",
    )
    shape = forms.ChoiceField(label="Forma", choices=SHAPES, widget=forms.RadioSelect)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = timezone.localdate()
        self.fields["start"].initial = today - datetime.timedelta(days=6)
        self.fields["end"].initial = today
        self.fields["shape"].initial = workbook.LONG
        for name in ("start", "end"):
            self.fields[name].widget.attrs["max"] = f"{today:%Y-%m-%d}"

    def clean(self):
        data = super().clean()
        if data.get("start") and data.get("end") and data["start"] > data["end"]:
            self.add_error("start", "Debe ser anterior o igual a la fecha final.")
        return data


def weekly_context():
    """Only the file of the Sunday before. While it is being prepared, or if it failed, also the
    last one that is ready, so there is always one to download."""
    latest = WeeklyExport.objects.first()
    weeks = [latest] if latest else []
    if latest and latest.status != WeeklyExport.Status.DONE:
        ready = WeeklyExport.objects.filter(status=WeeklyExport.Status.DONE).first()
        if ready:
            weeks.append(ready)
    return {"weeks": weeks, "preparing": any(week.status == WeeklyExport.Status.RUNNING for week in weeks)}


def page(request, form, status=200):
    context = {"form": form, "max_at_once": MAX_AT_ONCE}
    if request.user.is_admin:
        context.update(weekly_context())
    return render(request, "exports/index.html", context, status=status)


@reader_required
def index(request):
    return page(request, ExportForm())


@reader_required
def download(request):
    """The data of some laboratories (sources) and dates, in long or wide format, at once."""
    form = ExportForm(request.GET)
    if not form.is_valid():
        return page(request, form, status=400)
    first, last = form.cleaned_data["start"], form.cleaned_data["end"]
    sources = list(form.cleaned_data["sources"]) or None
    queryset = workbook.measurements(*day_span(first, last), sources=sources)
    total = queryset.count()
    if total > MAX_AT_ONCE:
        message = (
            f"Son {thousands(total)} mediciones; al momento se descargan hasta {thousands(MAX_AT_ONCE)}. "
            "Acorta las fechas o elige menos laboratorios."
        )
        if request.user.is_admin:
            message += " El archivo semanal tiene todos los datos."
        form.add_error(None, message)
        return page(request, form, status=400)
    shape = form.cleaned_data["shape"]
    names = ", ".join(source.code for source in sources) if sources else "todos los laboratorios"
    days = f"El {first:%Y-%m-%d}" if first == last else f"Del {first:%Y-%m-%d} al {last:%Y-%m-%d}"
    readme = workbook.readme_lines("Datos de calidad y operación de la PTAR (Dashboard PTAR).", f"{days}, {names}.", [shape])
    content = io.BytesIO()
    workbook.write(content, readme, [shape], queryset)
    content.seek(0)
    label = "largo" if shape == workbook.LONG else "ancho"
    which = "_".join(source.code.replace(" ", "-") for source in sources) if sources else "todos"
    dates = f"{first:%Y-%m-%d}" if first == last else f"{first:%Y-%m-%d}_{last:%Y-%m-%d}"
    return FileResponse(content, as_attachment=True, filename=f"datos_PTAR_{which}_{label}_{dates}.xlsx")


@admin_required
def weekly_list(request):
    """The weekly file, refreshed by HTMX while it is being prepared."""
    return render(request, "exports/_weekly.html", weekly_context())


@admin_required
def weekly_download(request, pk):
    export = get_object_or_404(WeeklyExport, pk=pk, status=WeeklyExport.Status.DONE)
    # Streamed in chunks from the storage: the whole history is tens of megabytes.
    response = StreamingHttpResponse(storage().chunks(export.file_name), content_type=XLSX)
    response["Content-Disposition"] = content_disposition_header(True, export.file_name)
    return response
