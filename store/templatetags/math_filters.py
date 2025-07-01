from django import template
from decimal import Decimal

register = template.Library()

@register.filter(name='divide')
def divide(value, arg):
    try:
        return Decimal(value) / Decimal(arg)
    except (ValueError, ZeroDivisionError, TypeError):
        return Decimal('0')

@register.filter(name='multiply')
def multiply(value, arg):
    try:
        return Decimal(value) * Decimal(arg)
    except (ValueError, TypeError):
        return Decimal('0')

@register.filter(name='percentage')
def percentage(value, total):
    try:
        return (Decimal(value) / Decimal(total)) * 100 if Decimal(total) != 0 else Decimal('0')
    except (ValueError, TypeError):
        return Decimal('0')