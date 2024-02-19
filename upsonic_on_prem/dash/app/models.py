from django.contrib.auth.models import AbstractUser
from django.db import models

from dash import settings

User = settings.AUTH_USER_MODEL
import uuid
from app.api_integration import API_Integration

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
    access_key = models.CharField(max_length=300, default="")

    def save(self, *args, **kwargs):
        self.the_register()
        super().save(*args, **kwargs)

    def the_register(self):
        if self.access_key == "":
            self.access_key = API_Integration.create_access_key()

    def add_user(self, id):
        API_Integration(id).add_user(self.access_key)
        API_Integration(id).set_name(self.access_key, self.username)
    def delete_user(self, id):
        API_Integration(id).delete_user(self.access_key)



    def __str__(self):
        return self.username

    def notify(self, title, message, important=False):
        notification = TheNotifications(title=title, message=message, important=important, owner=self)
        notification.save()
        self.notifications.add(notification)
        self.save()


    @property
    def is_admin(self):
        result = API_Integration(self.access_key).is_admin(self.access_key)
        return result if result != [None] else False