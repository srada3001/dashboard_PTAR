from django.core.management.base import BaseCommand, CommandError

from apps.accounts.models import User
from apps.imports.importer import ImportFailed, import_workbook
from apps.imports.maps import MapError

SUMMARY = [
    ("imported", "Mediciones importadas"),
    ("already_present", "Ya estaban en la base (iguales)"),
    ("existing_conflicts", "Ya estaban con otro valor (no se tocaron)"),
    ("suspect", "Dudosas (fuera del rango físico)"),
    ("qualified", "Con calificador (< o >)"),
    ("text_numbers", "Números escritos como texto"),
    ("nan", "No numéricos (NaN, no se importan)"),
    ("formula_cells", "Celdas con fórmula (no se importan)"),
    ("identical_duplicates", "Duplicados iguales (se importan una vez)"),
    ("conflicts", "Duplicados con valores distintos (no se importan)"),
    ("rounded_times", "Filas con la hora redondeada"),
    ("deduced_times", "Filas con la hora deducida por la secuencia"),
    ("dropped_rows", "Filas sin fecha válida (no se importan)"),
    ("dropped_values", "Valores de esas filas"),
    ("variables_created", "Variables creadas"),
    ("catalog_created", "Entradas del catálogo creadas"),
]


class Command(BaseCommand):
    help = (
        "Imports the historical Excel workbooks (docs/REQUISITOS.md §9): every Excel table with a map in "
        "import_maps/. Idempotent; --dry-run does everything and rolls it back. The full report is "
        "kept in the admin (Importación → Lotes de importación)."
    )

    def add_arguments(self, parser):
        parser.add_argument("files", nargs="+", help="Libros de Excel (.xlsx).")
        parser.add_argument("--dry-run", action="store_true", help="Simula: no guarda mediciones.")
        parser.add_argument("--table", action="append", dest="tables", help="Solo esta tabla de Excel (se puede repetir).")
        parser.add_argument("--user", help="Quién corre la importación. Por defecto, el único administrador.")

    def handle(self, *args, files, dry_run, tables, user, **options):
        person = self.person(user)
        for path in files:
            try:
                batches = import_workbook(path, person, dry_run=dry_run, tables=tables)
            except (ImportFailed, MapError, FileNotFoundError) as error:
                raise CommandError(str(error)) from error
            for batch in batches:
                self.print_batch(batch)

    def person(self, username):
        if username:
            person = User.objects.filter(username__iexact=username, is_active=True).first()
            if person is None:
                raise CommandError(f"No hay una persona activa con el usuario «{username}».")
            return person
        admins = list(User.objects.filter(role=User.Role.ADMIN, is_active=True)[:2])
        if len(admins) != 1:
            raise CommandError("Indica quién corre la importación con --user.")
        return admins[0]

    def print_batch(self, batch):
        mode = " (EN SECO: no se guardó nada)" if batch.dry_run else ""
        self.stdout.write(self.style.MIGRATE_HEADING(f"{batch.table} · hoja «{batch.sheet}»{mode}"))
        self.stdout.write(f"  Filas: {batch.counts.get('rows', 0)}")
        for key, label in SUMMARY:
            if batch.counts.get(key):
                self.stdout.write(f"  {label}: {batch.counts[key]}")
        for key, label in (("unmapped_headers", "Encabezados sin mapeo"), ("missing_headers", "Encabezados del mapeo que no están")):
            if batch.report.get(key):
                self.stdout.write(self.style.WARNING(f"  {label}: {', '.join(batch.report[key])}"))
        self.stdout.write(f"  Informe completo: Administración → Lotes de importación → #{batch.pk}")
