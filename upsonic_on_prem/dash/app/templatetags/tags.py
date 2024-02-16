from django import template

from dash import settings

register = template.Library()


# debug
@register.simple_tag(name='debug_mode')
def debug_mode():
    return settings.DEBUG
