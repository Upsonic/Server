from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from app import views

urlpatterns = [

    path('home', views.home, name="home"),
    path('notifications/', views.notifications, name="notifications"),
    path('notification_read/', views.notification_read_id, name="notification_read_id"),
    path('notification_read/<id>', views.notification_read_id, name="notification_read_id_sub"),

]
