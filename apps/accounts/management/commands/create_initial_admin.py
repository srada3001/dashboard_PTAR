import os
import secrets

from django.core.management.base import BaseCommand, CommandError

from apps.accounts.models import User

ENV_VAR = "PTAR_INITIAL_ADMIN"  # "username;Full Name", set by scripts/gcp/create-admin.sh


class Command(BaseCommand):
    help = (
        "Creates an administrator with a random temporary password, printed once. "
        "The person must replace it at first login. With --from-env it reads "
        f"{ENV_VAR} and does nothing if that username already exists (run at every startup): "
        "it never touches an existing account, so the variable can stay set."
    )

    def add_arguments(self, parser):
        parser.add_argument("username", nargs="?")
        parser.add_argument("full_name", nargs="?")
        parser.add_argument("--from-env", action="store_true")

    def handle(self, *args, username, full_name, from_env, **options):
        if from_env:
            value = os.environ.get(ENV_VAR, "").strip()
            if not value:
                return
            username, _, full_name = value.partition(";")
            username, full_name = username.strip(), full_name.strip()
            # Also after a database replacement (replace-db.sh) that left the person out.
            if User.objects.filter(username__iexact=username).exists():
                return

        if not username or not full_name:
            raise CommandError("Se necesitan el usuario y el nombre completo.")
        if User.objects.filter(username__iexact=username).exists():
            raise CommandError(f"Ya existe una persona con el usuario «{username}».")

        password = secrets.token_urlsafe(12)
        User.objects.create_superuser(username, full_name, password, must_change_password=True)
        self.stdout.write(f"Administrador «{username}» creado. Contraseña temporal: {password}")
        self.stdout.write("Deberá cambiarla en su primer ingreso.")
