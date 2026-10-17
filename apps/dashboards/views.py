from django.shortcuts import render

from apps.accounts.permissions import reader_required


@reader_required
def important_variables(request):
    """Phenols, temperature, pH, SST and G&A (docs/REQUISITOS.md §7.1). Built in phase 2."""
    return render(request, "dashboards/important_variables.html")


@reader_required
def explorer(request):
    """Any parameter, points and sources, with descriptive statistics (§7.2). Built in phase 2."""
    return render(request, "dashboards/explorer.html")
