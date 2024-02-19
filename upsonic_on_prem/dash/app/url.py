from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from app import views
from django.views.generic.base import RedirectView



urlpatterns = [

    path('home', views.home, name="home"),
    path('libraries', views.libraries, name="libraries"),
    path('control_library/<id>', views.control_library, name="control_library"),
    path('control_element/<id>', views.control_element, name="control_element"),
    path('control_user/<id>', views.control_user, name="control_user"),
    path('add_user', views.add_user, name="add_user"),
    path('delete_user/<id>', views.delete_user, name="delete_user"),
    path('enable_user/<id>', views.enable_user, name="enable_user"),
    path('disable_user/<id>', views.disable_user, name="disable_user"),
    path('enable_admin/<id>', views.enable_admin, name="enable_admin"),
    path('disable_admin/<id>', views.disable_admin, name="disable_admin"),
    path('community', views.community, name="community"),
    path('notifications/', views.notifications, name="notifications"),
    path('notification_read/', views.notification_read_id, name="notification_read_id"),
    path('notification_read/<id>', views.notification_read_id, name="notification_read_id_sub"),
    path('', RedirectView.as_view(url='/home', permanent=False), name='index')

]
