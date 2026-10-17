from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group

from apps.core.audit import AuditedAdmin
from apps.core.models import AuditEntry

from .forms import TemporaryPasswordForm, UserAdminChangeForm, UserAdminCreationForm
from .lockout import is_locked, unlock
from .models import User

# Permissions come from the role, not from Django groups.
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(AuditedAdmin, DjangoUserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    change_password_form = TemporaryPasswordForm

    list_display = ("username", "full_name", "role", "forms_summary", "is_active", "locked")
    list_filter = ("role", "is_active", "capture_forms")
    search_fields = ("username", "full_name")
    ordering = ("username",)
    filter_horizontal = ("capture_forms",)
    readonly_fields = ("last_login", "date_joined")
    actions = ["unlock_accounts"]

    fieldsets = (
        (None, {"fields": ("username", "full_name", "password")}),
        ("Rol y ámbito de captura", {"fields": ("role", "capture_forms")}),
        ("Estado", {"fields": ("is_active", "must_change_password")}),
        ("Fechas", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "description": "Una cuenta por persona, nunca compartida. La contraseña es temporal: "
                "la persona deberá cambiarla al entrar.",
                "fields": ("username", "full_name", "role", "capture_forms", "password1", "password2"),
            },
        ),
    )

    @admin.display(description="formatos de captura")
    def forms_summary(self, obj):
        if obj.is_admin:
            return "Todos"
        return ", ".join(form.name for form in obj.capture_forms.all()) or "—"

    @admin.display(boolean=True, description="bloqueada")
    def locked(self, obj):
        return is_locked(obj.username)

    @admin.action(description="Desbloquear las cuentas seleccionadas")
    def unlock_accounts(self, request, queryset):
        for user in queryset:
            unlock(user.username)
        self.message_user(request, f"{queryset.count()} cuenta(s) desbloqueada(s).", messages.SUCCESS)

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("capture_forms")

    def user_change_password(self, request, id, form_url=""):
        response = super().user_change_password(request, id, form_url)
        if request.method == "POST" and response.status_code == 302:
            user = self.get_object(request, id)
            AuditEntry.record(request.user, AuditEntry.Action.UPDATE, user, {"Contraseña": ["", "temporal asignada"]})
        return response

    # People are deactivated, never deleted, so their history is kept.
    def has_delete_permission(self, request, obj=None):
        return False
