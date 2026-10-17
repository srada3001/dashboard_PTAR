"""Role checks for views. They run on the server for every request: hiding a menu link is not
enough, since anyone can type a URL (docs/REQUISITOS.md §4 and §12)."""

from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def reader_required(view):
    """Views, charts and exports: administrators and engineers. Capturers read nothing."""

    @login_required
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.can_read:
            raise PermissionDenied
        return view(request, *args, **kwargs)

    return wrapper


def capture_required(view):
    """Capture pages: administrators, capturers, and engineers with at least one capture form."""

    @login_required
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.can_capture:
            raise PermissionDenied
        return view(request, *args, **kwargs)

    return wrapper
