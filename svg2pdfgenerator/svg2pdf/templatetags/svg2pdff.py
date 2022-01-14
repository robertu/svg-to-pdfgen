from django import template

register = template.Library()

@register.filter
def hight(value):
    return float(value * 0.7)

@register.filter
def floatf(value):
    return '%.2f' % float(value)

@register.filter
def opistabeli(value):
    return (value + 12) * -1

@register.filter
def kwadrat(value):
    return value + 25
