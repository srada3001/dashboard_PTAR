"""The capture grid of a form for a day (docs/REQUISITOS.md §6).

Each variable has the cells of its frequency: one per hour, 07:00 and 16:00, only 07:00 (BIOTA),
a. m. and p. m., or one for the whole day. A form with hourly variables (Ecolab) shows the hours as rows and the variables as
columns, like today's sheet; the others show the variables as rows and their few cells as columns.
A form may have sections (BIOTA: «Fase I» and, below it, «DIAPAC»), shown one below the other; the
variables of a point always go together within their section, whatever their order in the admin.

Who may change a value that is already there: the administrator, any; the engineer, any value of
their forms registered in the last 48 hours; the capturer, only their own captures of the last 48
hours. Who may fill an empty cell: the administrator, any; the engineer and the capturer, only
samples of the last 48 hours. Only the administrator has no time limit (decided on 2026-11-09;
before, the engineer had none and the capturer had 24 hours to correct). Anyone with the form sees
every value of the day, so nothing is typed twice or overwritten.
"""

import datetime
from dataclasses import dataclass, field

from django.utils import timezone

from apps.accounts.models import User
from apps.catalog.models import Schedule
from apps.measurements.models import Measurement, TimePrecision, period_start
from apps.measurements.records import version
from apps.measurements.values import format_number

# How far back an engineer or a capturer may correct captures and fill empty cells.
EDIT_WINDOW = datetime.timedelta(hours=48)
# More time columns than this, and they go in rows (the 24 hours of Ecolab). Without hourly
# variables there are at most five: 07:00, 16:00, a. m., p. m. and the day (BIOTA).
CELLS_AS_COLUMNS = 5


@dataclass(frozen=True)
class Slot:
    key: str  # "h07", "am", "pm" or "d"
    label: str
    precision: str
    hour: int | None = None

    def taken_at(self, day):
        if self.precision == TimePrecision.HOUR:
            return timezone.make_aware(datetime.datetime.combine(day, datetime.time(self.hour)))
        return period_start(day, self.precision)


HOURS = [Slot(f"h{hour:02}", f"{hour:02}:00", TimePrecision.HOUR, hour) for hour in range(24)]
MORNING = Slot("am", "a. m.", TimePrecision.AM)
AFTERNOON = Slot("pm", "p. m.", TimePrecision.PM)
WHOLE_DAY = Slot("d", "Día", TimePrecision.DAY)
SLOTS = {slot.key: slot for slot in [*HOURS, MORNING, AFTERNOON, WHOLE_DAY]}
ORDER = list(SLOTS)

SLOTS_BY_FREQUENCY = {
    Schedule.HOURLY: HOURS,
    Schedule.TWICE_DAILY: [HOURS[7], HOURS[16]],
    Schedule.MORNING: [HOURS[7]],
    Schedule.AM_PM: [MORNING, AFTERNOON],
    Schedule.DAILY: [WHOLE_DAY],
    Schedule.OCCASIONAL: [WHOLE_DAY],
}


def slots_of(variable):
    return SLOTS_BY_FREQUENCY.get(variable.time_resolution, [WHOLE_DAY])


def display(measurement):
    """'<0,1', '7,3': the value as it is typed."""
    return f"{measurement.qualifier}{format_number(measurement.value)}" if measurement else ""


def may_change(user, measurement, now):
    """(allowed, why not) for correcting or deleting a value that is already there."""
    if measurement is None or user.is_admin:
        return True, ""
    recent = measurement.created_at >= now - EDIT_WINDOW
    if user.role == User.Role.ENGINEER:
        if recent:
            return True, ""
        return False, "Solo puedes corregir capturas de las últimas 48 horas; más atrás, el administrador."
    own = measurement.created_by_id == user.pk and measurement.updated_by_id in (None, user.pk)
    if own and recent:
        return True, ""
    return False, "Solo puedes corregir tus propias capturas de las últimas 48 horas."


def may_add(user, taken_at, now):
    """(allowed, why not) for filling an empty cell: by the time of its sample."""
    if user.is_admin or taken_at >= now - EDIT_WINDOW:
        return True, ""
    return False, "Solo puedes llenar datos de las últimas 48 horas."


def may_write(user, measurement, taken_at, now):
    """(allowed, why not) for a cell: correcting what is there, or filling it when it is empty."""
    return may_change(user, measurement, now) if measurement is not None else may_add(user, taken_at, now)


def note(measurement):
    """Who registered a value and when, as the cell's tooltip says it."""
    if measurement is None:
        return ""
    when = lambda moment: f"{timezone.localtime(moment):%Y-%m-%d %H:%M}"  # noqa: E731
    text = f"Registrado por {measurement.created_by.display_name} el {when(measurement.created_at)}"
    if measurement.updated_by_id:
        text += f"; corregido por {measurement.updated_by.display_name} el {when(measurement.updated_at)}"
    text += "."
    if measurement.suspect:
        text = "Dudoso: fuera del rango físico, sin revisar. Corrígelo o bórralo. " + text
    return text


@dataclass
class Cell:
    variable: object
    slot: Slot
    taken_at: datetime.datetime | None = None
    measurement: Measurement | None = None
    applies: bool = True  # the variable has this cell
    future: bool = False
    locked: str = ""  # why it cannot be changed

    @property
    def value(self):
        return display(self.measurement)

    @property
    def version(self):
        return version(self.measurement)

    @property
    def readonly(self):
        return self.future or bool(self.locked)

    @property
    def title(self):
        if self.future:
            return "Todavía no: es una hora futura."
        return " ".join(part for part in (note(self.measurement), self.locked) if part)

    @property
    def suspect(self):
        return bool(self.measurement and self.measurement.suspect)


@dataclass
class Grid:
    form: object
    day: datetime.date
    variables: list
    slots: list
    cells: dict = field(default_factory=dict)  # {(variable id, slot key): Cell}
    sections: dict = field(default_factory=dict)  # {variable id: section name}

    @property
    def slots_as_rows(self):
        return len(self.slots) > CELLS_AS_COLUMNS

    def cell(self, variable, slot):
        return self.cells.get((variable.pk, slot.key)) or Cell(variable, slot, applies=False)

    def point_groups(self):
        """[(point, number of consecutive variables at it, its CSS classes)], for the header of the
        hours layout. Every other point is shaded, and each one after the first starts with a
        thicker border, so the eye finds the point's columns."""
        groups = []
        for variable in self.variables:
            if groups and groups[-1][0] == variable.point:
                groups[-1][1] += 1
            else:
                groups.append([variable.point, 1])
        return [(point, span, column_classes(index, True)) for index, (point, span) in enumerate(groups)]

    def column_classes(self):
        """The CSS classes of each variable's column in the hours layout (see point_groups)."""
        classes, group = [], -1
        for index, variable in enumerate(self.variables):
            starts = not index or self.variables[index - 1].point != variable.point
            group += starts
            classes.append(column_classes(group, starts))
        return classes

    def variables_with_columns(self):
        """[(variable, its column's CSS classes)], for the parameters' header of the hours layout."""
        return list(zip(self.variables, self.column_classes()))

    def slot_rows(self):
        """[(slot, [(cell, its column's CSS classes) per variable], the row's CSS classes)]: the
        hours as rows, with a stronger line every 6 hours."""
        columns = self.column_classes()
        return [
            (
                slot,
                [(self.cell(variable, slot), css) for variable, css in zip(self.variables, columns)],
                "rejilla__cada-6" if slot.hour and slot.hour % 6 == 0 else "",
            )
            for slot in self.slots
        ]

    def section(self, variable):
        return self.sections.get(variable.pk, "")

    def variable_rows(self):
        """[(variable, rows of its point or 0 when not the first, [cell per slot], section title
        when the variable starts a section or "")]."""
        group = lambda variable: (self.section(variable), variable.point)  # noqa: E731
        rows = []
        for index, variable in enumerate(self.variables):
            previous = self.variables[index - 1] if index else None
            span = 0
            if previous is None or group(previous) != group(variable):
                span = 1
                while index + span < len(self.variables) and group(self.variables[index + span]) == group(variable):
                    span += 1
            title = ""
            if self.section(variable) and (previous is None or self.section(previous) != self.section(variable)):
                title = self.section(variable)
            rows.append((variable, span, [self.cell(variable, slot) for slot in self.slots], title))
        return rows


def column_classes(group, starts):
    """The shade of the point's columns (every other point) and the border where a point starts."""
    classes = []
    if group % 2:
        classes.append("rejilla__banda")
    if starts and group:
        classes.append("rejilla__inicio-col")
    return " ".join(classes)


def grouped(items):
    """The items of a form with each section together, and within it each point together, in the
    order they first appear."""
    first_section, first_point = {}, {}
    for index, item in enumerate(items):
        first_section.setdefault(item.section, index)
        first_point.setdefault((item.section, item.variable.point_id), index)
    return sorted(items, key=lambda item: (first_section[item.section], first_point[(item.section, item.variable.point_id)]))


def build(form, day, user, now=None):
    now = now or timezone.now()
    items = grouped(list(form.items.select_related("variable__point__area", "variable__parameter", "variable__source")))
    variables = [item.variable for item in items]
    keys = {slot.key for variable in variables for slot in slots_of(variable)}
    slots = [SLOTS[key] for key in ORDER if key in keys]
    grid = Grid(form=form, day=day, variables=variables, slots=slots, sections={item.variable_id: item.section for item in items})
    instants = {slot.key: slot.taken_at(day) for slot in slots}
    existing = {
        (m.variable_id, m.taken_at): m
        for m in Measurement.objects.filter(variable__in=variables, taken_at__in=set(instants.values()))
        .select_related("created_by", "updated_by")
    }
    for variable in variables:
        for slot in slots_of(variable):
            taken_at = instants[slot.key]
            measurement = existing.get((variable.pk, taken_at))
            grid.cells[(variable.pk, slot.key)] = Cell(
                variable=variable,
                slot=slot,
                taken_at=taken_at,
                measurement=measurement,
                future=taken_at > now,
                locked=may_write(user, measurement, taken_at, now)[1],
            )
    return grid

