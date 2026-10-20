"""The capture grid of a form for a day (docs/REQUISITOS.md §6).

Each variable has the cells of its frequency: one per hour, 07:00 and 16:00, a. m. and p. m., or one
for the whole day. A form with many hours (Nalco) shows the hours as rows and the variables as
columns, like today's sheet; the others show the variables as rows and their few cells as columns.

Who may change a value that is already there: the administrator and the engineer, any value of
their forms; the capturer, only their own captures of the last 24 hours (decided on 2026-10-20).
Anyone with the form sees every value of the day, so nothing is typed twice or overwritten.
"""

import datetime
from dataclasses import dataclass, field

from django.utils import timezone

from apps.accounts.models import User
from apps.catalog.models import Schedule
from apps.measurements.models import Measurement, TimePrecision, period_start
from apps.measurements.records import version
from apps.measurements.values import format_number

EDIT_WINDOW = datetime.timedelta(hours=24)
# More cells per variable than this, and the cells go in rows (the hours of Nalco).
CELLS_AS_COLUMNS = 3


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
    if measurement is None or user.role in (User.Role.ADMIN, User.Role.ENGINEER):
        return True, ""
    own = measurement.created_by_id == user.pk and measurement.updated_by_id in (None, user.pk)
    if own and measurement.created_at >= now - EDIT_WINDOW:
        return True, ""
    return False, "Solo puedes corregir tus propias capturas de las últimas 24 horas."


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

    @property
    def slots_as_rows(self):
        return len(self.slots) > CELLS_AS_COLUMNS

    def cell(self, variable, slot):
        return self.cells.get((variable.pk, slot.key)) or Cell(variable, slot, applies=False)

    def point_groups(self):
        """[(point, number of consecutive variables at it)], for the header of the hours layout."""
        groups = []
        for variable in self.variables:
            if groups and groups[-1][0] == variable.point:
                groups[-1][1] += 1
            else:
                groups.append([variable.point, 1])
        return groups

    def slot_rows(self):
        """[(slot, [cell per variable])]: the hours as rows."""
        return [(slot, [self.cell(variable, slot) for variable in self.variables]) for slot in self.slots]

    def variable_rows(self):
        """[(variable, rows of its point or 0 when not the first, [cell per slot])]."""
        rows = []
        for index, variable in enumerate(self.variables):
            first = index == 0 or self.variables[index - 1].point != variable.point
            span = 0
            if first:
                span = 1
                while index + span < len(self.variables) and self.variables[index + span].point == variable.point:
                    span += 1
            rows.append((variable, span, [self.cell(variable, slot) for slot in self.slots]))
        return rows


def build(form, day, user, now=None):
    now = now or timezone.now()
    variables = [
        item.variable
        for item in form.items.select_related("variable__point__area", "variable__parameter", "variable__source")
    ]
    keys = {slot.key for variable in variables for slot in slots_of(variable)}
    slots = [SLOTS[key] for key in ORDER if key in keys]
    grid = Grid(form=form, day=day, variables=variables, slots=slots)
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
                locked=may_change(user, measurement, now)[1],
            )
    return grid

