from django.urls import path

from . import views

urlpatterns = [
    path("variables-importantes/", views.important_variables, name="important_variables"),
    path("explorador/", views.explorer, name="explorer"),
]
