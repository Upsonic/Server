from django import template

from dash import settings

from app.api_integration import API_Integration

from app.pages import pages

register = template.Library()


# debug
@register.simple_tag(name="debug_mode")
def debug_mode():
    return settings.DEBUG


@register.simple_tag(name="sentry")
def sentry():
    return settings.sentry


@register.simple_tag(name="sentry_dsn")
def sentry_dsn():
    return settings.sentry_dsn


# debug
@register.simple_tag(name="default_ai_model")
def default_ai_model(request):
    return API_Integration(request.user.access_key).get_default_ai_model()


@register.simple_tag(name="pages", takes_context=True)
def pages_tag(context):
    request = context["request"]
    if request.user.is_admin:
        return pages
    else:
        return []


@register.simple_tag(name="pages_len", takes_context=True)
def pages_len(context):
    request = context["request"]
    if request.user.is_admin:
        return len(pages)
    else:
        return 0
