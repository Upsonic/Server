from django.contrib.auth.models import AbstractUser
from django.db import models

from dash import settings

User = settings.AUTH_USER_MODEL
import uuid
from app.api_integration import API_Integration
from dash.logs import logger
import threading

from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=".env")
import time

from django_currentuser.middleware import get_current_user


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
    dark_mode = models.BooleanField(default=True, blank=True, null=True)
    register = models.BooleanField(default=True, blank=True, null=True)
    ldap = models.BooleanField(default=False, blank=True, null=True)


    def save(self, *args, **kwargs):
        self.the_register()
        if self.register:
            try:
                currently_user_id = get_current_user().access_key
                self.add_user(currently_user_id)
            except:
                print("Passed registering process")
            self.register = False
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

    def full_access(self, scope):
        if API_Integration(self.access_key).is_admin(self.access_key):
            return True

        all_scopes = API_Integration(self.access_key).get_read_scopes_of_me()

        control = False

        if scope + ".*" in all_scopes:
            control = True

        return control

    def full_access_write(self, scope):
        if API_Integration(self.access_key).is_admin(self.access_key):
            return True

        all_scopes = API_Integration(self.access_key).get_write_scopes_of_me()

        control = False

        logger.info(all_scopes)

        if scope + ".*" in all_scopes:
            control = True

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
        notification = TheNotifications(
            title=title, message=message, important=important, owner=self
        )
        notification.save()
        self.notifications.add(notification)
        self.save()

    @property
    def is_admin(self):
        result = API_Integration(self.access_key).is_admin(self.access_key)
        return result if result != [None] else False


active_tasks = []
pending_tasks = []
parallel_ai_task_limit = int(os.getenv("parallel_ai_task_limit", 2))


# Write a thread function that starts and control the pending tasks and moving to activa tasks. I want to set limit to os.getenv("parallel_ai_tasks")
def organizer_ai_tasks():
    global active_tasks
    global pending_tasks
    global parallel_ai_task_limit
    while True:
        len_of_active_tasks = len(active_tasks)
        suitable_space = parallel_ai_task_limit - len_of_active_tasks
        if suitable_space > 0:
            the_tasks = pending_tasks[:suitable_space]
            for i in the_tasks:
                active_tasks.append(i)
                pending_tasks.remove(i)
                i.start()
        for i in active_tasks:
            if not i.is_alive():
                active_tasks.remove(i)

        time.sleep(1)


organizer_thread = None


class AI_Task(models.Model):
    task_name = models.CharField(max_length=1000)
    access_key = models.CharField(max_length=2000)
    key = models.CharField(max_length=2000)
    status = models.BooleanField(default=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    not_start_task = models.BooleanField(default=False, null=True, blank=True)

    user_input = models.TextField(null=True, blank=True)
    ai_output = models.TextField(null=True, blank=True)

    def sub_func(self, func):
        func(self.key)
        self.status = True
        self.save()
        if self.owner is not None:
            self.owner.notify(
                "Task finished",
                "The task "
                + self.task_name
                + " for "
                + self.key
                + " has been finished",
            )

    def documentation_task(self):
        the_func = API_Integration(self.access_key).create_documentation
        the_thread = threading.Thread(target=self.sub_func, args=(the_func,))
        pending_tasks.append(the_thread)



    def time_complexity_task(self):
        the_func = API_Integration(self.access_key).create_time_complexity
        the_thread = threading.Thread(target=self.sub_func, args=(the_func,))
        pending_tasks.append(the_thread)



    def tags_task(self):
        the_func = API_Integration(self.access_key).create_tags
        the_thread = threading.Thread(target=self.sub_func, args=(the_func,))
        pending_tasks.append(the_thread)


    def readme_task(self):
        the_func = API_Integration(self.access_key).create_readme
        the_thread = threading.Thread(target=self.sub_func, args=(the_func,))
        pending_tasks.append(the_thread)

    def the_register(self):
        if self.status:
            return
        any_task = True
        not_start_task = self.not_start_task
        print("FROM MODEL: ", not_start_task)
        if self.task_name == "documentation":
            self.documentation_task() if not not_start_task else None

        elif self.task_name == "time_complexity":
            self.time_complexity_task() if not not_start_task else None

        elif self.task_name == "tags":
            self.tags_task() if not not_start_task else None

        elif self.task_name == "readme":
            self.readme_task() if not not_start_task else None
        else:
            any_task = False

        if any_task:
            if self.owner is not None:
                self.owner.notify(
                    "Task started",
                    "The task "
                    + self.task_name
                    + " for "
                    + self.key
                    + " has been started",
                )

    def save(self, *args, **kwargs):
        global organizer_thread
        if organizer_thread is None:
            organizer_thread = threading.Thread(target=organizer_ai_tasks)
            organizer_thread.start()

        self.the_register()
        super().save(*args, **kwargs)
