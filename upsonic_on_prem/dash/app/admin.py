from django.contrib import admin
from app import models

# Register your models here.
admin.site.register(models.User)
admin.site.register(models.AI_Task)
admin.site.register(models.TheNotifications)
