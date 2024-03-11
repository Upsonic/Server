from django import template

from dash import settings

from app.api_integration import API_Integration

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

# debug
@register.simple_tag(name='default_ai_model')
def default_ai_model(request):
    return API_Integration(request.user.access_key).get_default_ai_model() 