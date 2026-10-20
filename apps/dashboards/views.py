import datetime
from urllib.parse import urlencode

from django import forms
from django.db.models import Max
from django.contrib import messages
from django.http import FileResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from apps.accounts.permissions import reader_required
from apps.exports.templatetags.exports import thousands
from apps.exports.views import MAX_AT_ONCE
from apps.measurements.models import Measurement

from . import export
from .explorer import ExplorerForm, explore
from .models import MAX_POINTS
from .panels import CHART_DAYS, DAILY_MEANS_FROM, DEFAULT_CHART_DAYS, build_cards


class WindowForm(forms.Form):
    end = forms.DateField(label="Hasta", required=False, widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"))
    days = forms.TypedChoiceField(
        label="Gráficas", coerce=int, required=False,
        choices=[(days, f"Últimos {days} días" + (" (promedios diarios)" if days >= DAILY_MEANS_FROM else "")) for days in CHART_DAYS],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["end"].initial = timezone.localdate()
        self.fields["end"].widget.attrs["max"] = f"{timezone.localdate():%Y-%m-%d}"
        self.fields["days"].initial = DEFAULT_CHART_DAYS

    def clean_end(self):
        end = self.cleaned_data["end"]
        if end and end > timezone.localdate():
            raise forms.ValidationError("No puede ser una fecha futura.")
        return end

    def window(self):
        """(last day, chart days): what was asked when valid, else today and the default."""
        if self.is_bound and self.is_valid():
            return self.cleaned_data["end"] or self.fields["end"].initial, self.cleaned_data["days"] or DEFAULT_CHART_DAYS
        return self.fields["end"].initial, DEFAULT_CHART_DAYS


@reader_required
def important_variables(request):
    """Phenols, temperature, pH, SST and G&A, as configured in the admin (docs/REQUISITOS.md §7.1)."""
    form = WindowForm(request.GET or None)
    last_day, chart_days = form.window()
    context = {"form": form, "cards": build_cards(last_day, chart_days), "last_day": last_day}

    # Before the capture starts (phase 3) the newest data are some days old: say so, and offer them.
    newest = Measurement.objects.filter(suspect=False, taken_at__lt=timezone.now()).aggregate(newest=Max("taken_at"))["newest"]
    if newest is not None:
        newest_day = timezone.localtime(newest).date()
        if newest_day < last_day - datetime.timedelta(days=6):
            context["newest_day"] = newest_day
            context["newest_url"] = f"?{urlencode({'end': newest_day.isoformat(), 'days': chart_days})}"
    return render(request, "dashboards/important_variables.html", context)


@reader_required
def explorer(request):
    """Any parameter, points and sources, with descriptive statistics (§7.2)."""
    form = ExplorerForm(request.GET or None)
    exploration = explore(form.cleaned_data) if form.is_bound and form.is_valid() else None
    return render(request, "dashboards/explorer.html", {
        "form": form, "exploration": exploration, "max_points": MAX_POINTS, "query": request.GET.urlencode(),
    })


@reader_required
def explorer_options(request):
    """The points and sources of a parameter, for the explorer's form (HTMX)."""
    # Unbound: a parameter just chosen is not an error for having no points yet.
    form = ExplorerForm(initial={"parameter": request.GET.get("parameter")})
    return render(request, "dashboards/_explorer_options.html", {"form": form, "max_points": MAX_POINTS})


@reader_required
def explorer_export(request):
    """What the explorer shows, as an Excel workbook."""
    form = ExplorerForm(request.GET or None)
    if not (form.is_bound and form.is_valid()):
        return redirect(f"{reverse('explorer')}?{request.GET.urlencode()}")
    total = export.measurement_count(form.cleaned_data)
    if total > MAX_AT_ONCE:
        messages.error(request, (
            f"Son {thousands(total)} mediciones; al momento se descargan hasta {thousands(MAX_AT_ONCE)}. "
            "Acorta las fechas o usa el archivo semanal de Exportaciones, que tiene todos los datos."
        ))
        return redirect(f"{reverse('explorer')}?{request.GET.urlencode()}")
    exploration = explore(form.cleaned_data)
    return FileResponse(export.workbook(exploration), as_attachment=True, filename=export.filename(exploration))
