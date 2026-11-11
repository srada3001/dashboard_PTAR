from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="exports"),
    path("descargar/", views.download, name="exports_download"),
    path("semanales/", views.weekly_list, name="exports_weekly"),
    path("semanales/<int:pk>/", views.weekly_download, name="exports_weekly_download"),
]
