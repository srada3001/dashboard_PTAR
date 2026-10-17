from django.contrib.auth.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from .models import User


class UserAdminCreationForm(UserCreationForm):
    """Admin form to create a person with a temporary password."""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "full_name", "role", "capture_forms")


class UserAdminChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = ("username", "full_name", "role", "capture_forms", "is_active", "must_change_password")


class TemporaryPasswordForm(AdminPasswordChangeForm):
    """Password set by an administrator is temporary: the person must replace it on next login."""

    def save(self, commit=True):
        self.user.must_change_password = True
        return super().save(commit=commit)
