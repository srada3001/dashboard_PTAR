from django.core.management.base import BaseCommand

from apps.exports import weekly
from apps.exports.models import WeeklyExport


class Command(BaseCommand):
    help = (
        "Prepares this week's export now (all the data up to last Sunday), if it is not ready. "
        "The app does it by itself on the first request after Monday 00:00 (docs/REQUISITOS.md §10)."
    )

    def handle(self, *args, **options):
        export = weekly.ensure_current(background=False)
        if export is None:
            current = WeeklyExport.objects.filter(week=weekly.due_week()).first()
            self.stdout.write(f"Nada que hacer: {current} está «{current.get_status_display()}».")
        elif export.status == WeeklyExport.Status.DONE:
            self.stdout.write(self.style.SUCCESS(f"{export.file_name}: {export.measurements} mediciones, {export.size} bytes."))
        else:
            self.stderr.write(f"Falló: {export.error}")
