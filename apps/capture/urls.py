from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="capture_index"),
    path("<int:pk>/", views.grid, name="capture_grid"),
    path("<int:pk>/celda/", views.save_cell, name="capture_save_cell"),
    path("<int:pk>/historial/", views.cell_history, name="capture_cell_history"),
]
