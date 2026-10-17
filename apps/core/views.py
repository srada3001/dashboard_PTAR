from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


@login_required
def home(request):
    """Each role lands on its first page: readers on the main view, capturers on Capture."""
    if request.user.can_read:
        return redirect("important_variables")
    return redirect("capture_index")
