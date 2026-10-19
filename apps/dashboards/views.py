from django.shortcuts import render

from apps.accounts.permissions import reader_required
from apps.measurements.models import Measurement


def pending_page(request, template):
    """Until phase 2 builds the charts, the page says how much data is already there."""
    return render(request, template, {"measurement_count": Measurement.objects.count()})


@reader_required
def important_variables(request):
    """Phenols, temperature, pH, SST and G&A (docs/REQUISITOS.md §7.1). Built in phase 2."""
    return pending_page(request, "dashboards/important_variables.html")


@reader_required
def explorer(request):
    """Any parameter, points and sources, with descriptive statistics (§7.2). Built in phase 2."""
    return pending_page(request, "dashboards/explorer.html")
