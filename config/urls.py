from django.contrib import admin
from django.contrib.staticfiles.storage import staticfiles_storage
from django.shortcuts import redirect
from django.urls import include, path

admin.site.site_header = "Dashboard PTAR — Administración"
admin.site.site_title = "Dashboard PTAR"
admin.site.index_title = "Administración"


def favicon(request):
    """Browsers ask for /favicon.ico on pages without our template (errors, admin)."""
    return redirect(staticfiles_storage.url("img/favicon.ico"), permanent=True)


urlpatterns = [
    path("favicon.ico", favicon),
    path("", include("apps.core.urls")),
    path("", include("apps.accounts.urls")),
    path("", include("apps.dashboards.urls")),
    path("captura/", include("apps.capture.urls")),
    path("exportaciones/", include("apps.exports.urls")),
    path("admin/", admin.site.urls),
]
