from django import template

register = template.Library()

@register.filter
def div(a, b):
    try:
        return int(a) / int(b) if int(b) != 0 else 0
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def mul(a, b):
    try:
        return int(a) * int(b)
    except (ValueError, TypeError):
        return 0
