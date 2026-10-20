import datetime
import io

from django import forms
from django.http import FileResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.http import content_disposition_header

from apps.accounts.permissions import reader_required
from apps.catalog.models import Source
from apps.dashboards.stats import day_span

from . import workbook
from .models import WeeklyExport
from .storage import XLSX, storage
from .templatetags.exports import thousands

# What can be downloaded at once: Firebase cuts requests longer than 60 seconds. More data is in
# the weekly file, which has all of it.
MAX_AT_ONCE = 100_000
RECENT_WEEKS = 8


class ExportForm(forms.Form):
    start = forms.DateField(label="Desde", widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"))
    end = forms.DateField(label="Hasta", widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"))
    sources = forms.ModelMultipleChoiceField(
        Source.objects.all(), label="Fuentes", required=False, widget=forms.CheckboxSelectMultiple,
        help_text="Ninguna marcada: todas.",
    )
    shape = forms.ChoiceField(label="Forma", choices=workbook.SHAPES, widget=forms.RadioSelect)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = timezone.localdate()
        self.fields["start"].initial = today - datetime.timedelta(days=29)
        self.fields["end"].initial = today
        self.fields["shape"].initial = workbook.LONG

    def clean(self):
        data = super().clean()
        if data.get("start") and data.get("end") and data["start"] > data["end"]:
            self.add_error("start", "Debe ser anterior a la fecha final.")
        return data


def weekly_context():
    weeks = list(WeeklyExport.objects.all()[:RECENT_WEEKS])
    return {"weeks": weeks, "preparing": any(week.status == WeeklyExport.Status.RUNNING for week in weeks)}


def page(request, form, status=200):
    context = {"form": form, "max_at_once": MAX_AT_ONCE, **weekly_context()}
    return render(request, "exports/index.html", context, status=status)


@reader_required
def index(request):
    return page(request, ExportForm())


@reader_required
def weekly_list(request):
    """The weekly files, refreshed by HTMX while one is being prepared."""
    return render(request, "exports/_weekly.html", weekly_context())


@reader_required
def weekly_download(request, pk):
    export = get_object_or_404(WeeklyExport, pk=pk, status=WeeklyExport.Status.DONE)
    # Streamed in chunks from the storage: the whole history is tens of megabytes.
    response = StreamingHttpResponse(storage().chunks(export.file_name), content_type=XLSX)
    response["Content-Disposition"] = content_disposition_header(True, export.file_name)
    return response


@reader_required
def download(request):
    """The data of some days and sources, in long or wide format, at once."""
    form = ExportForm(request.GET)
    if not form.is_valid():
        return page(request, form, status=400)
    first, last = form.cleaned_data["start"], form.cleaned_data["end"]
    sources = list(form.cleaned_data["sources"]) or None
    queryset = workbook.measurements(*day_span(first, last), sources=sources)
    total = queryset.count()
    if total > MAX_AT_ONCE:
        form.add_error(None, (
            f"Son {thousands(total)} mediciones; al momento se descargan hasta {thousands(MAX_AT_ONCE)}. "
            "Acorta las fechas, elige menos fuentes o usa el archivo semanal, que tiene todos los datos."
        ))
        return page(request, form, status=400)
    shape = form.cleaned_data["shape"]
    names = ", ".join(source.code for source in sources) if sources else "todas las fuentes"
    readme = workbook.readme_lines(
        "Datos de calidad y operación de la PTAR (Dashboard PTAR).",
        f"Del {first:%Y-%m-%d} al {last:%Y-%m-%d}, {names}.",
        [shape],
    )
    content = io.BytesIO()
    workbook.write(content, readme, [shape], queryset)
    content.seek(0)
    label = "largo" if shape == workbook.LONG else "ancho"
    return FileResponse(content, as_attachment=True, filename=f"datos_PTAR_{label}_{first:%Y-%m-%d}_{last:%Y-%m-%d}.xlsx")
