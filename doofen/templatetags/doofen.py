from django import template

register = template.Library()

@register.filter
def multi(value,arg):
    return value * arg

@register.filter
def itemneedx(value):
    if value:
        return value.replace(',|','<br>')
    else:
        return '空'
