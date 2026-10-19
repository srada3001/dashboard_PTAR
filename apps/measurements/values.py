"""What a measurement value may be, shared by the historical import and, later, the capture.

A value is a number written with a decimal comma or point, optionally preceded by "<" or ">"
("<0,1" is below 0.1, usually the laboratory's detection limit). Anything else ("7,,4", "ND",
"asdfdf") is not a value: there is no state for "no data", the value simply does not exist
(docs/REQUISITOS.md §5 and §6).
"""

import re
from dataclasses import dataclass

NUMBER = re.compile(r"^\s*([<>])?\s*(-?(?:\d+(?:[.,]\d+)?|[.,]\d+))\s*$")


class InvalidValue(ValueError):
    pass


@dataclass(frozen=True)
class ParsedValue:
    qualifier: str  # "", "<" or ">"
    value: float


def parse_value(text):
    """'7,4' → ('', 7.4); '< 0,1' → ('<', 0.1). Raises InvalidValue for anything else."""
    match = NUMBER.match(text)
    if not match:
        raise InvalidValue("Solo números, con coma o punto decimal, opcionalmente con «<» o «>» delante.")
    qualifier, number = match.groups()
    return ParsedValue(qualifier or "", float(number.replace(",", ".")))


def outside(value, low, high):
    """Whether a value falls outside an optional range; a missing end is no bound."""
    return (low is not None and value < low) or (high is not None and value > high)


def outside_physical_range(parameter, value):
    """Impossible for the parameter (pH 73): rejected when captured, marked suspect when imported."""
    return outside(value, parameter.physical_min, parameter.physical_max)


def outside_typical_range(variable, value):
    """Unusual for the variable: the capture asks to confirm it."""
    return outside(value, variable.typical_min, variable.typical_max)


def format_number(value, decimals=None):
    """A number as people read it here: decimal comma, and no trailing zeros when decimals is None."""
    if decimals is not None:
        text = f"{value:.{decimals}f}"
    else:
        text = f"{value:.6f}".rstrip("0").rstrip(".")
    return text.replace(".", ",")
