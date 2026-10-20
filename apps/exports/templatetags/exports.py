from django import template

register = template.Library()


@register.filter
def thousands(number):
    """636297 → '636.297', as numbers are read here."""
    return f"{number:,}".replace(",", ".")
