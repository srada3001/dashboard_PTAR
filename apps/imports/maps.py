"""The versioned import maps in import_maps/: the initial catalog and one map per Excel table.

They hold headers and catalog codes only, never plant data (CLAUDE.md). A map has one row per
column of its Excel table, found by its header (not its position):

    header,action,point,parameter,source,time,frequency,note

- action: "date" (the sampling date), "import" or "skip" (the note says why);
- time: "row" (the hour written in the row, hourly tables), "07:00" / "16:00", "am" / "pm"
  (only the half of the day is known) or "day" (only the day is known);
- frequency: the variable's frequency when the import creates it; empty means it follows the time.

Line breaks inside an Excel header are written as the two characters "\\n".
"""

import csv
import datetime
from dataclasses import dataclass
from pathlib import Path

from django.conf import settings

from apps.catalog.models import Schedule
from apps.measurements.models import TimePrecision

MAPS_DIR = Path(settings.BASE_DIR) / "import_maps"
CATALOG_DIR = MAPS_DIR / "catalog"

ACTIONS = ("date", "import", "skip")
FIXED_HOURS = {"07:00": datetime.time(7), "16:00": datetime.time(16)}
PERIODS = {"am": TimePrecision.AM, "pm": TimePrecision.PM, "day": TimePrecision.DAY}
TIMES = ("row", *FIXED_HOURS, *PERIODS)
DEFAULT_FREQUENCY = {
    "row": Schedule.HOURLY, "07:00": Schedule.TWICE_DAILY, "16:00": Schedule.TWICE_DAILY,
    "am": Schedule.AM_PM, "pm": Schedule.AM_PM, "day": Schedule.DAILY,
}


class MapError(ValueError):
    pass


def escape_header(header):
    """An Excel header as written in the maps: line breaks become the two characters "\\n"."""
    return str(header).replace("\r\n", "\n").replace("\n", "\\n")


@dataclass(frozen=True)
class ColumnMap:
    header: str
    action: str
    point: str = ""
    parameter: str = ""
    source: str = ""
    time: str = ""
    frequency: str = ""
    note: str = ""

    @property
    def variable_key(self):
        return (self.point, self.parameter, self.source)

    @property
    def variable_label(self):
        return f"{self.point} · {self.parameter} · {self.source}"


@dataclass
class TableMap:
    table: str
    columns: list

    @property
    def by_header(self):
        return {column.header: column for column in self.columns}

    @property
    def hourly(self):
        """Tables whose rows carry the hour (table 1): their timeline is checked row by row."""
        return any(column.time == "row" for column in self.columns if column.action == "import")


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def read_table_map(path):
    path = Path(path)
    columns, seen = [], set()
    for line, row in enumerate(read_csv(path), start=2):
        column = ColumnMap(**{key: (value or "") for key, value in row.items()})
        where = f"{path.name}, línea {line}"
        if column.header in seen:
            raise MapError(f"{where}: el encabezado «{column.header}» está repetido.")
        seen.add(column.header)
        if column.action not in ACTIONS:
            raise MapError(f"{where}: acción «{column.action}» desconocida; debe ser {', '.join(ACTIONS)}.")
        if column.action == "import":
            if not (column.point and column.parameter and column.source):
                raise MapError(f"{where}: faltan el punto, el parámetro o la fuente.")
            if column.time not in TIMES:
                raise MapError(f"{where}: hora «{column.time}» desconocida; debe ser {', '.join(TIMES)}.")
            if column.frequency and column.frequency not in Schedule.values:
                raise MapError(f"{where}: frecuencia «{column.frequency}» desconocida.")
        columns.append(column)
    if sum(column.action == "date" for column in columns) != 1:
        raise MapError(f"{path.name}: debe tener exactamente una columna de fecha.")
    return TableMap(table=path.stem, columns=columns)


def available_maps(directory=MAPS_DIR):
    """{Excel table name: map file} for every map in the folder."""
    return {path.stem: path for path in sorted(Path(directory).glob("*.csv"))}
