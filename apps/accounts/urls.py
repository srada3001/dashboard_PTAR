from django.contrib.auth import views as auth_views
from django.urls import path

from .views import PasswordChangeView

urlpatterns = [
    path("entrar/", auth_views.LoginView.as_view(redirect_authenticated_user=True), name="login"),
    path("salir/", auth_views.LogoutView.as_view(), name="logout"),
    path("contrasena/", PasswordChangeView.as_view(), name="password_change"),
]
