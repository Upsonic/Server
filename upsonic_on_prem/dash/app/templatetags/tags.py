from django import template

from dash import settings

from app.api_integration import API_Integration

from app.pages import pages

register = template.Library()


# debug
@register.simple_tag(name="debug_mode")
def debug_mode():
    return settings.DEBUG


@register.simple_tag(name="demo_mode")
def demo_mode():
    return settings.DEMO_MODE

@register.simple_tag(name="yc_mode")
def yc_mode():
    return settings.YC_MODE


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


@register.simple_tag(name="notifications", takes_context=True)
def notifications_tag(context):
    request = context["request"]
    the_notifications = request.user.notifications.filter(read=False)
    for each in the_notifications:
        each.read = True
        each.save()
    return the_notifications


@register.simple_tag(name="pages_len", takes_context=True)
def pages_len(context):
    request = context["request"]
    if request.user.is_admin:
        return len(pages)
    else:
        return 0
