from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse

from django.http.response import HttpResponse


# Create your views here.
@login_required
def home(request, exception=None):
    request.user.notify("Welcome to Upsonic", "Your free cloud is ready, you can start using it now.")
    return render(request, "templates/home.html",
                  {"page_title": "Home"})


def notifications(request):
    the_notifications_of_the_user = request.user.notifications.filter(read=False)
    json_notifications = []
    for notification in the_notifications_of_the_user:
        json_notifications.append({"id": notification.id, "title": notification.title, "message": notification.message,
                                   "date": notification.date, "read": notification.read,
                                   "important": notification.important})
        if not notification.important:
            notification.read = True
        notification.save()
    return JsonResponse(json_notifications, safe=False)


def notification_read_id(request, id):
    notification = request.user.notifications.get(id=id)
    notification.read = True
    notification.save()
    return HttpResponse(status=200)
