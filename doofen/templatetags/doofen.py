from django import template

register = template.Library()

@register.filter
def multi(value,arg):
    if value and arg:
        return value * arg
    else:
        return '空'

@register.filter
def itemneedx(value):
    if value:
        return value.replace(',|','<br>')
    else:
        return '空'
