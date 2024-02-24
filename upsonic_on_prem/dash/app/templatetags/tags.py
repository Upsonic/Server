from django import template

from dash import settings

register = template.Library()


# debug
@register.simple_tag(name='debug_mode')
def debug_mode():
    return settings.DEBUG


@register.simple_tag(name='sentry')
def sentry():

    return settings.sentry

@register.simple_tag(name='sentry_dsn')
def sentry_dsn():

    return settings.sentry_dsn