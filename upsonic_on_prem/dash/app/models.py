from django.contrib.auth.models import AbstractUser
from django.db import models

from dash import settings

User = settings.AUTH_USER_MODEL
import uuid


class TheNotifications(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    message = models.CharField(max_length=1000)
    date = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    important = models.BooleanField(default=False)

    def __str__(self):
        return self.title + " - " + str(self.date)


class User(AbstractUser):
    notifications = models.ManyToManyField(TheNotifications, blank=True)
    def __str__(self):
        return self.username

    def notify(self, title, message, important=False):
        notification = TheNotifications(title=title, message=message, important=important, owner=self)
        notification.save()
        self.notifications.add(notification)
        self.save()
