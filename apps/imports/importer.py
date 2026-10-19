"""The historical import (docs/REQUISITOS.md §9): Excel tables → measurements, with a report.

For each mapped table of a workbook:
1. the initial catalog is loaded (only what is missing is created);
2. each row gets its sampling time (timeline.py), each mapped cell is read: numbers and clean
   numeric texts ("5.6", "<10") are values; codes and typos (SB, ND, "7,,4") are NaN and are not
   imported; formulas are computed, not measured, and are not imported either;
3. duplicates: the same value twice for a variable and time is imported once; different values
   are not imported at all, and both go to the report;
4. values outside the parameter's physical range are imported as suspect;
5. what already is in the database is never changed: the same value counts as already present,
   another value is reported.
Every measurement created leaves its "create" history row, with the batch. A dry run does all of
it inside a transaction that is rolled back, so its report is exactly what a real run would do.
"""

import datetime
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from django.db import transaction
from django.utils import timezone

from apps.catalog.models import Variable
from apps.core.models import AuditEntry
from apps.measurements.models import (
    Measurement,
    MeasurementHistory,
    Origin,
    TimePrecision,
    format_taken_at,
    period_start,
)
from apps.measurements.values import InvalidValue, ParsedValue, format_number, outside_physical_range, parse_value

from .catalog import IMPORT_NOTE, CatalogIndex, CatalogLoader
from .maps import CATALOG_DIR, DEFAULT_FREQUENCY, FIXED_HOURS, MAPS_DIR, PERIODS, available_maps, escape_header, read_table_map
from .models import ImportBatch
from .timeline import daily_timeline, hourly_timeline
from .workbook import find_tables, read_table, sha256

HISTORY_REASON = "Importación del histórico"
BATCH_SIZE = 2000


class ImportFailed(Exception):
    pass


@dataclass
class Candidate:
    column: object  # ColumnMap
    row: int
    taken_at: datetime.datetime
    precision: str
    qualifier: str
    value: float

    @property
    def key(self):
        return (self.column.variable_key, self.taken_at)


def show_written(value):
    if isinstance(value, datetime.datetime):
        text = f"{value:%Y-%m-%d %H:%M:%S}"
        return text[:-3] if text.endswith(":00") else text
    if isinstance(value, datetime.date):
        return f"{value:%Y-%m-%d}"
    return "" if value is None else str(value)


def show_value(qualifier, value):
    return f"{qualifier}{format_number(value)}"


def read_cell(cell):
    """('blank'|'formula'|'number'|'text_number'|'nan', ParsedValue or None)."""
    value = cell.value
    if cell.formula:
        return "formula", None
    if value is None or (isinstance(value, str) and not value.strip()):
        return "blank", None
    if isinstance(value, bool):
        return "nan", None
    if isinstance(value, (int, float)):
        return "number", ParsedValue("", float(value))
    if isinstance(value, str):
        try:
            return "text_number", parse_value(value)
        except InvalidValue:
            return "nan", None
    return "nan", None  # dates and times Excel put in a value cell


class TableImporter:
    def __init__(self, data, table_map, index, now):
        self.data = data
        self.map = table_map
        self.index = index
        self.now = now
        self.counts = defaultdict(int)
        self.report = defaultdict(list)
        self.column_stats = {}

    # -- Analysis (no writes) ------------------------------------------------------------------

    def analyse(self):
        headers = [escape_header(h) for h in self.data.headers]
        by_header = self.map.by_header
        self.report["unmapped_headers"] = [h for h in headers if h not in by_header]
        self.report["missing_headers"] = [c.header for c in self.map.columns if c.header not in headers]

        date_column = next(c for c in self.map.columns if c.action == "date")
        if date_column.header not in headers:
            raise ImportFailed(f"La tabla {self.map.table} no tiene la columna de fecha «{date_column.header}».")
        date_index = headers.index(date_column.header)

        columns = []
        for index, header in enumerate(headers):
            column = by_header.get(header)
            if column is None:
                continue
            self.column_stats[header] = {
                "header": header, "action": column.action, "note": column.note,
                "variable": column.variable_label if column.action == "import" else "",
                "values": 0, "imported": 0, "nan": 0, "formulas": 0,
            }
            if column.action == "import":
                missing = self.index.missing(column)
                if missing:
                    raise ImportFailed(f"Columna «{header}»: no están en el catálogo: {', '.join(missing)}.")
                columns.append((index, column))
            elif column.action == "skip":
                self.counts["skipped_columns"] += 1

        local_now = timezone.localtime(self.now).replace(tzinfo=None)
        written = [cells[date_index].value for _, cells in self.data.rows]
        if self.map.hourly:
            timeline = hourly_timeline(written, local_now)
        else:
            timeline = daily_timeline(written, local_now.date())

        candidates = []
        self.counts["rows"] = len(self.data.rows)
        for (row, cells), time in zip(self.data.rows, timeline.rows):
            row_values = 0
            for index, column in columns:
                kind, parsed = read_cell(cells[index])
                stats = self.column_stats[column.header]
                if kind == "blank":
                    continue
                if kind == "formula":
                    stats["formulas"] += 1
                    self.counts["formula_cells"] += 1
                    continue
                if kind == "nan":
                    stats["nan"] += 1
                    self.counts["nan"] += 1
                    self.report["nan_values"].append({
                        "row": row, "date": show_written(time.written), "header": column.header,
                        "value": show_written(cells[index].value),
                    })
                    continue
                if kind == "text_number":
                    self.counts["text_numbers"] += 1
                stats["values"] += 1
                row_values += 1
                if time.when is not None:
                    taken_at, precision = self.sampling_time(time.when, column.time)
                    candidates.append(Candidate(column, row, taken_at, precision, parsed.qualifier, parsed.value))
            if not row_values:
                continue  # empty rows (some are created ahead of time) are not worth reporting
            if time.when is None:
                self.counts["dropped_rows"] += 1
                self.counts["dropped_values"] += row_values
                self.report["dropped_rows"].append({
                    "row": row, "date": show_written(time.written), "reason": time.reason, "values": row_values,
                })
            else:
                if time.deduced:
                    self.counts["deduced_times"] += 1
                    self.report["deduced_times"].append({
                        "row": row, "written": show_written(time.written), "deduced": show_written(time.when),
                    })
                elif time.rounded:
                    self.counts["rounded_times"] += 1
        self.resolved = self.resolve_duplicates(candidates)
        return self

    def sampling_time(self, when, time):
        if time == "row":
            return timezone.make_aware(when), TimePrecision.HOUR
        day = when.date() if isinstance(when, datetime.datetime) else when
        if time in FIXED_HOURS:
            return timezone.make_aware(datetime.datetime.combine(day, FIXED_HOURS[time])), TimePrecision.HOUR
        precision = PERIODS[time]
        return period_start(day, precision), precision

    def resolve_duplicates(self, candidates):
        groups = defaultdict(list)
        for candidate in candidates:
            groups[candidate.key].append(candidate)
        resolved = []
        for group in groups.values():
            first = group[0]
            if all((c.qualifier, c.value, c.precision) == (first.qualifier, first.value, first.precision) for c in group):
                resolved.append(first)
                self.counts["identical_duplicates"] += len(group) - 1
                continue
            self.counts["conflicts"] += 1
            self.counts["conflict_values"] += len(group)
            self.report["conflicts"].append({
                "variable": first.column.variable_label,
                "taken_at": format_taken_at(first.taken_at, first.precision),
                "values": [{"row": c.row, "header": c.column.header, "value": show_value(c.qualifier, c.value)} for c in group],
            })
        resolved.sort(key=lambda c: (c.row, c.column.header))
        return resolved

    # -- Writing -------------------------------------------------------------------------------

    def write(self, user, batch):
        variables = {}
        for candidate in self.resolved:
            key = candidate.column.variable_key
            if key not in variables:
                variables[key] = self.variable_for(candidate.column, user)

        existing = {
            (m["variable_id"], m["taken_at"]): (m["value"], m["qualifier"])
            for m in Measurement.objects.filter(variable__in=list(variables.values()))
            .values("variable_id", "taken_at", "value", "qualifier")
        }
        new = []
        for candidate in self.resolved:
            variable = variables[candidate.column.variable_key]
            present = existing.get((variable.pk, candidate.taken_at))
            if present is not None:
                if present == (candidate.value, candidate.qualifier):
                    self.counts["already_present"] += 1
                else:
                    self.counts["existing_conflicts"] += 1
                    self.report["existing_conflicts"].append({
                        "variable": str(variable),
                        "taken_at": format_taken_at(candidate.taken_at, candidate.precision),
                        "existing": show_value(present[1], present[0]),
                        "new": show_value(candidate.qualifier, candidate.value),
                        "row": candidate.row,
                    })
                continue
            suspect = outside_physical_range(variable.parameter, candidate.value)
            measurement = Measurement(
                variable=variable, taken_at=candidate.taken_at, time_precision=candidate.precision,
                value=candidate.value, qualifier=candidate.qualifier, suspect=suspect,
                origin=Origin.HISTORY, created_by=user,
            )
            new.append(measurement)
            self.column_stats[candidate.column.header]["imported"] += 1
            item = {
                "row": candidate.row, "header": candidate.column.header,
                "taken_at": format_taken_at(candidate.taken_at, candidate.precision),
                "value": show_value(candidate.qualifier, candidate.value),
            }
            if suspect:
                parameter = variable.parameter
                item["range"] = range_text(parameter.physical_min, parameter.physical_max)
                self.report["suspect_values"].append(item)
            if candidate.qualifier:
                self.report["qualified_values"].append(item)

        Measurement.objects.bulk_create(new, batch_size=BATCH_SIZE)
        MeasurementHistory.objects.bulk_create(
            [
                MeasurementHistory(
                    measurement=m, variable=m.variable, taken_at=m.taken_at, time_precision=m.time_precision,
                    action=MeasurementHistory.Action.CREATE, new_value=m.value, new_qualifier=m.qualifier,
                    new_suspect=m.suspect, user=user, reason=HISTORY_REASON, batch=batch,
                )
                for m in new
            ],
            batch_size=BATCH_SIZE,
        )
        self.counts["imported"] = len(new)
        self.counts["suspect"] = len(self.report["suspect_values"])
        self.counts["qualified"] = len(self.report["qualified_values"])
        return self

    def variable_for(self, column, user):
        point, parameter, source = self.index.resolve(column)
        variable = Variable.objects.select_related("parameter").filter(point=point, parameter=parameter, source=source).first()
        if variable is None:
            variable = Variable(
                point=point, parameter=parameter, source=source,
                time_resolution=column.frequency or DEFAULT_FREQUENCY[column.time],
            )
            variable.full_clean()
            variable.save()
            AuditEntry.record(user, AuditEntry.Action.CREATE, variable, IMPORT_NOTE)
            self.report["variables_created"].append(str(variable))
            self.counts["variables_created"] += 1
        return variable


def range_text(low, high):
    if low is None:
        return f"≤ {format_number(high)}"
    if high is None:
        return f"≥ {format_number(low)}"
    return f"{format_number(low)} – {format_number(high)}"


def import_workbook(path, user, *, dry_run=False, tables=None, now=None, maps_dir=MAPS_DIR, catalog_dir=CATALOG_DIR):
    """Imports every mapped table of a workbook (or only `tables`); one ImportBatch per table."""
    path = Path(path)
    found = find_tables(path)
    maps = available_maps(maps_dir)
    names = [name for name in maps if name in found and (not tables or name in tables)]
    if tables:
        unknown = sorted(set(tables) - set(names))
        if unknown:
            raise ImportFailed(f"El archivo no tiene estas tablas con mapeo: {', '.join(unknown)}.")
    if not names:
        raise ImportFailed(f"{path.name} no tiene ninguna tabla de Excel con mapeo en import_maps/.")
    digest = sha256(path)
    return [
        import_table(path, digest, found[name], read_table_map(maps[name]), user,
                     dry_run=dry_run, now=now, catalog_dir=catalog_dir)
        for name in names
    ]


def import_table(path, digest, table, table_map, user, *, dry_run, now=None, catalog_dir=CATALOG_DIR):
    started = timezone.now()
    now = now or started
    data = read_table(path, table)
    batch = ImportBatch(
        file_name=Path(path).name, file_sha256=digest, sheet=table.sheet, table=table.name,
        dry_run=dry_run, run_by=user, started_at=started, finished_at=started,
    )
    with transaction.atomic():
        loader = CatalogLoader(user, catalog_dir).load()
        importer = TableImporter(data, table_map, CatalogIndex(), now).analyse()
        batch.save()
        importer.write(user, batch)
        if dry_run:
            transaction.set_rollback(True)

    importer.counts["catalog_created"] = len(loader.created)
    report = dict(importer.report)
    report["catalog_created"] = loader.created
    report["catalog_warnings"] = loader.warnings
    report["columns"] = list(importer.column_stats.values())
    batch.counts = dict(importer.counts)
    batch.report = report
    batch.finished_at = timezone.now()
    if dry_run:
        batch.pk = None
        batch._state.adding = True
        batch.save()
    else:
        batch.save(update_fields=["counts", "report", "finished_at"])
    return batch
