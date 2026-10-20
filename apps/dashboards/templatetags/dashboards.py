from django import template

from apps.measurements.models import format_taken_at
from apps.measurements.values import format_number

register = template.Library()


@register.filter
def num(value, decimals=None):
    """7.25 → '7,25' with the parameter's decimals; nothing for a missing value."""
    if value is None:
        return ""
    return format_number(value, decimals)


@register.filter
def taken(sample):
    """When a sample was taken: '2026-10-07 16:00', '2026-10-07 a. m.' or '2026-10-07'."""
    return format_taken_at(sample.taken_at, sample.precision)
