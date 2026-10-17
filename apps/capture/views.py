from django.shortcuts import render

from apps.accounts.permissions import capture_required


@capture_required
def index(request):
    """The capture forms this person may fill. The grids themselves arrive in phase 3."""
    forms = request.user.allowed_capture_forms().select_related("source").prefetch_related("items")
    return render(request, "capture/index.html", {"capture_forms": forms})
