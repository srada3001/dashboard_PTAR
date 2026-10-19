"""Loads the initial catalog of import_maps/catalog/ (sources, areas, points, parameters).

Only what is missing is created; existing entries are never changed, since from then on the
catalog is edited in the admin. Every creation leaves an AuditEntry, as admin changes do.
"""

from django.db.models.functions import Lower

from apps.catalog.models import Parameter, PointAlias, ProcessArea, SamplingPoint, Source
from apps.core.models import AuditEntry

from .maps import CATALOG_DIR, read_csv

IMPORT_NOTE = {"Creado por": ["", "la importación del histórico"]}


def optional_float(text):
    text = (text or "").strip()
    return float(text) if text else None


class CatalogLoader:
    def __init__(self, user, directory=CATALOG_DIR):
        self.user = user
        self.directory = directory
        self.created = []  # "Punto BA-4001", for the report
        self.warnings = []

    def create(self, model, **fields):
        obj = model(**fields)
        obj.full_clean()
        obj.save()
        AuditEntry.record(self.user, AuditEntry.Action.CREATE, obj, IMPORT_NOTE)
        self.created.append(f"{str(model._meta.verbose_name).capitalize()} «{obj}»")
        return obj

    @staticmethod
    def find(model, field, value):
        return model.objects.annotate(_key=Lower(field)).filter(_key=value.strip().lower()).first()

    def load(self):
        for row in read_csv(self.directory / "sources.csv"):
            if not self.find(Source, "code", row["code"]):
                self.create(Source, code=row["code"], name=row["name"], description=row["description"] or "")

        for row in read_csv(self.directory / "areas.csv"):
            if not self.find(ProcessArea, "name", row["name"]):
                self.create(ProcessArea, name=row["name"], order=int(row["order"]))

        for row in read_csv(self.directory / "points.csv"):
            point = self.find(SamplingPoint, "code", row["code"])
            if point is None:
                area = self.find(ProcessArea, "name", row["area"]) if row["area"] else None
                point = self.create(SamplingPoint, code=row["code"], name=row["name"] or "", area=area,
                                    order=int(row["order"] or 0))
            for alias in filter(None, (a.strip() for a in (row["aliases"] or "").split("|"))):
                existing = self.find(PointAlias, "alias", alias)
                if existing is None:
                    self.create(PointAlias, point=point, alias=alias)
                elif existing.point_id != point.pk:
                    self.warnings.append(f"El alias «{alias}» ya es de {existing.point}; no se asignó a {point}.")

        for row in read_csv(self.directory / "parameters.csv"):
            if not self.find(Parameter, "code", row["code"]):
                self.create(
                    Parameter, code=row["code"], name=row["name"], unit=row["unit"] or "",
                    decimals=int(row["decimals"] or 2),
                    physical_min=optional_float(row["physical_min"]), physical_max=optional_float(row["physical_max"]),
                )
        return self


class CatalogIndex:
    """Looks up catalog entries by code, ignoring case; points also by alias."""

    def __init__(self):
        self.sources = {s.code.lower(): s for s in Source.objects.all()}
        self.parameters = {p.code.lower(): p for p in Parameter.objects.all()}
        self.points = {p.code.lower(): p for p in SamplingPoint.objects.all()}
        for alias in PointAlias.objects.select_related("point"):
            self.points.setdefault(alias.alias.lower(), alias.point)

    def missing(self, column):
        """What a map column names that is not in the catalog."""
        missing = []
        if column.point.lower() not in self.points:
            missing.append(f"punto «{column.point}»")
        if column.parameter.lower() not in self.parameters:
            missing.append(f"parámetro «{column.parameter}»")
        if column.source.lower() not in self.sources:
            missing.append(f"fuente «{column.source}»")
        return missing

    def resolve(self, column):
        return (
            self.points[column.point.lower()],
            self.parameters[column.parameter.lower()],
            self.sources[column.source.lower()],
        )
