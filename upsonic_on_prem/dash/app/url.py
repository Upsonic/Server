from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from app import views
from django.views.generic.base import RedirectView



urlpatterns = [

    path('home', views.home, name="home"),
    path('community', views.community, name="community"),
    path('notifications/', views.notifications, name="notifications"),
    path('notification_read/', views.notification_read_id, name="notification_read_id"),
    path('notification_read/<id>', views.notification_read_id, name="notification_read_id_sub"),
    path('', RedirectView.as_view(url='/home', permanent=False), name='index')

]
