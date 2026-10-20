from django.urls import path

from . import views

urlpatterns = [
    path("variables-importantes/", views.important_variables, name="important_variables"),
    path("explorador/", views.explorer, name="explorer"),
    path("explorador/opciones/", views.explorer_options, name="explorer_options"),
    path("explorador/exportar/", views.explorer_export, name="explorer_export"),
]
