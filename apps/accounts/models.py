from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.db.models.functions import Lower
from django.utils import timezone

# Spanish name particles stay lowercase inside a name: "María de los Ángeles".
NAME_PARTICLES = {"de", "del", "la", "las", "los", "y", "e"}


def capitalize_name(name):
    """Each word of a name with its first letter in uppercase ("juan sebastián rada rey" →
    "Juan Sebastián Rada Rey"); hyphenated parts too. Only first letters change, so names
    typed with capitals keep them."""
    words = []
    for index, word in enumerate(name.split()):
        if index > 0 and word.lower() in NAME_PARTICLES:
            words.append(word.lower())
        else:
            words.append("-".join(part[:1].upper() + part[1:] for part in word.split("-")))
    return " ".join(words)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, username, full_name, password=None, **extra_fields):
        if not username:
            raise ValueError("El usuario es obligatorio.")
        user = self.model(username=username, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, full_name, password=None, **extra_fields):
        extra_fields.setdefault("role", User.Role.ADMIN)
        extra_fields.setdefault("must_change_password", False)
        return self.create_user(username, full_name, password, **extra_fields)


class User(AbstractBaseUser):
    """One account per person, never shared: the history must say who registered each value.

    Three roles (docs/REQUISITOS.md §4):
    - administrator: reads and captures everything, and manages users, catalogs and limits;
    - engineer: reads everything and captures only in their capture forms (none: read-only);
    - capturer: captures only in their capture forms and **reads nothing**.
    People are deactivated, never deleted, so their history is kept.
    """

    class Role(models.TextChoices):
        ADMIN = "admin", "Administrador"
        ENGINEER = "engineer", "Ingeniero"
        CAPTURER = "capturer", "Capturista"

    username = models.CharField(
        "usuario",
        max_length=30,
        unique=True,
        validators=[UnicodeUsernameValidator()],
        help_text="Nombre corto de la persona; se usa para entrar a la app. Una cuenta por persona, nunca compartida.",
        error_messages={"unique": "Ya existe una persona con ese usuario."},
    )
    full_name = models.CharField("nombre completo", max_length=150)
    role = models.CharField(
        "rol",
        max_length=20,
        choices=Role.choices,
        default=Role.CAPTURER,
        help_text="Administrador: todo. Ingeniero: lee todo y captura en sus formatos. "
        "Capturista: solo captura en sus formatos, sin acceso de lectura.",
    )
    capture_forms = models.ManyToManyField(
        "catalog.CaptureForm",
        blank=True,
        related_name="users",
        verbose_name="formatos de captura",
        help_text="Los formatos que puede llenar (su ámbito de captura). El administrador puede llenarlos todos.",
    )
    is_active = models.BooleanField(
        "activo",
        default=True,
        help_text="Desmarcar en lugar de borrar cuando la persona ya no usa la app.",
    )
    must_change_password = models.BooleanField(
        "debe cambiar la contraseña",
        default=True,
        help_text="Se le pedirá una contraseña nueva en su próximo ingreso.",
    )
    date_joined = models.DateTimeField("fecha de creación", default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["full_name"]

    class Meta:
        verbose_name = "persona"
        verbose_name_plural = "personas"
        ordering = ["username"]
        constraints = [
            models.UniqueConstraint(
                Lower("username"),
                name="user_username_unique",
                violation_error_message="Ya existe una persona con ese usuario.",
            ),
        ]

    def __str__(self):
        return self.username

    @property
    def display_name(self):
        """The full name as shown everywhere."""
        return capitalize_name(self.full_name)

    def get_full_name(self):
        return self.display_name

    def get_short_name(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def can_read(self):
        """Views, charts and exports. A capturer never reads."""
        return self.role in (self.Role.ADMIN, self.Role.ENGINEER)

    def allowed_capture_forms(self):
        from apps.catalog.models import CaptureForm

        if self.is_admin:
            return CaptureForm.objects.all()
        return self.capture_forms.all()

    @property
    def can_capture(self):
        """Engineers only capture when they have capture forms; capturers always land on Capture,
        even with none assigned yet, because it is the only page they have."""
        if self.role == self.Role.ENGINEER:
            return self.capture_forms.exists()
        return True

    # Django admin checks these; an administrator has every permission.
    @property
    def is_staff(self):
        return self.is_admin

    @property
    def is_superuser(self):
        return self.is_admin

    def has_perm(self, perm, obj=None):
        return self.is_active and self.is_admin

    def has_perms(self, perm_list, obj=None):
        return all(self.has_perm(perm, obj) for perm in perm_list)

    def has_module_perms(self, app_label):
        return self.is_active and self.is_admin
