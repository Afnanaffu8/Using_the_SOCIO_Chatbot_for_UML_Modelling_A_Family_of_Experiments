from django import template

register = template.Library()

@register.filter
def sum_list(value):
    try:
        return sum(value)
    except Exception:
        return 0

@register.filter
def divide(value, arg):
    try:
        return float(value) / float(arg)
    except Exception:
        return 0
