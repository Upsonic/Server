from django.contrib.auth.models import AbstractUser
from django.db import models

from dash import settings

User = settings.AUTH_USER_MODEL
import uuid
from app.api_integration import API_Integration

import threading


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


    def can_write(self, scope):
        if API_Integration(self.access_key).is_admin(self.access_key):
            return True
        all_scopes = API_Integration(self.access_key).get_write_scopes_of_me()
        
        control = False

        for i in all_scopes:
            if scope == i:
                control = True
                break
            elif scope.startswith(i[:-1]) and i.endswith("*"):
                control = True
                break

        return control        



    def can_read(self, scope):
        if API_Integration(self.access_key).is_admin(self.access_key):
            return True
        all_scopes = API_Integration(self.access_key).get_read_scopes_of_me()
        
        control = False

        for i in all_scopes:
            if scope == i:
                control = True
                break
            elif scope.startswith(i[:-1]) and i.endswith("*"):
                control = True
                break

        return control        


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


ai_threads = []


class AI_Task(models.Model):
    task_name = models.CharField(max_length=1000)
    access_key = models.CharField(max_length=2000)
    key = models.CharField(max_length=2000)
    status = models.BooleanField(default=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def sub_func(self, func):
            func(self.key)
            self.status = True
            self.save()
            if self.owner is not None:
                self.owner.notify("Task finished", "The task " + self.task_name + " for " + self.key + " has been finished")

    def documentation_task(self):
        the_func = API_Integration(self.access_key).create_documentation
        the_thread = threading.Thread(target=self.sub_func, args=(the_func,))
        the_thread.start()
        ai_threads.append(the_thread)
    def mistakes_task(self):
        the_func = API_Integration(self.access_key).create_mistakes
        the_thread = threading.Thread(target=self.sub_func, args=(the_func,))
        the_thread.start()
        ai_threads.append(the_thread)
    def time_complexity_task(self):
        the_func = API_Integration(self.access_key).create_time_complexity
        the_thread = threading.Thread(target=self.sub_func, args=(the_func,))
        the_thread.start()
        ai_threads.append(the_thread)
    def required_test_types_task(self):
        the_func = API_Integration(self.access_key).create_required_test_types
        the_thread = threading.Thread(target=self.sub_func, args=(the_func,))
        the_thread.start()
        ai_threads.append(the_thread)
    def tags_task(self):
        the_func = API_Integration(self.access_key).create_tags
        the_thread = threading.Thread(target=self.sub_func, args=(the_func,))
        the_thread.start()
        ai_threads.append(the_thread)        
    def security_analysis_task(self):
        the_func = API_Integration(self.access_key).create_security_analysis
        the_thread = threading.Thread(target=self.sub_func, args=(the_func,))
        the_thread.start()
        ai_threads.append(the_thread)



    def the_register(self):
        if self.status:
            return
        any_task = True
        if self.task_name == "documentation":
            self.documentation_task()
        elif self.task_name == "mistakes":
            self.mistakes_task()
        elif self.task_name == "time_complexity":
            self.time_complexity_task()
        elif self.task_name == "required_test_types":
            self.required_test_types_task()
        elif self.task_name == "tags":
            self.tags_task()
        elif self.task_name == "security_analysis":
            self.security_analysis_task()
        else:
            any_task = False
        
        if any_task:
            if self.owner is not None:
                self.owner.notify("Task started", "The task " + self.task_name + " for " + self.key + " has been started")


    def save(self, *args, **kwargs):
        self.the_register()
        super().save(*args, **kwargs)

