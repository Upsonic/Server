from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from app import views
from django.views.generic.base import RedirectView



urlpatterns = [

    path('home', views.home, name="home"),
    path('libraries', views.libraries, name="libraries"),
    path('control_library/<id>', views.control_library, name="control_library"),
    path('control_library_settings/<id>', views.control_library_settings, name="control_library_settings"),
    path('control_library_version/<id>', views.control_library_version, name="control_library_version"),
    path('control_library_version_create/<id>', views.control_library_version_create, name="control_library_version_create"),
    path('control_library_version_delete/<id>/<version>', views.control_library_version_delete, name="control_library_version_delete"),
    path('control_element/<id>', views.control_element, name="control_element"),
    path('control_element_dependency/<id>', views.control_element_dependency, name="control_element_dependency"),
    path('control_element_runs/<id>', views.control_element_runs, name="control_element_runs"),
    path('control_element_runs_analyze/<id>/<run_sha>', views.control_element_runs_analyze, name="control_element_runs_analyze"),
    path('control_element_settings/<id>', views.control_element_settings, name="control_element_settings"),
    path('control_element_commits/<id>', views.control_element_commits, name="control_element_commits"),
    path('control_element_version/<id>', views.control_element_version, name="control_element_version"),
    path('control_element_version_create/<id>', views.control_element_version_create, name="control_element_version_create"),
    path('control_element_version_delete/<id>/<version>', views.control_element_version_delete, name="control_element_version_delete"),
    path('regenerate_documentation/<id>', views.regenerate_documentation, name="regenerate_documentation"),
    path('activate_usage_analyses/<id>', views.activate_usage_analyses, name="activate_usage_analyses"),
    path('activate_usage_analyses_prefix/<id>', views.activate_usage_analyses_prefix, name="activate_usage_analyses_prefix"),
    path('deactivate_usage_analyses_prefix/<id>', views.deactivate_usage_analyses_prefix, name="deactivate_usage_analyses_prefix"),
    path('deactivate_usage_analyses/<id>', views.deactivate_usage_analyses, name="deactivate_usage_analyses"),
    path('regenerate_readme/<id>', views.regenerate_readme, name="regenerate_readme"),
    path('delete_scope/<id>', views.delete_scope, name="delete_scope"),
    path('control_user/<id>', views.control_user, name="control_user"),
    path('analyze_user/<id>', views.analyze_user, name="analyze_user"),
    path('add_user', views.add_user, name="add_user"),
    path('profile', views.profile, name="profile"),
    path('delete_user/<id>', views.delete_user, name="delete_user"),
    path('enable_user/<id>', views.enable_user, name="enable_user"),
    path('disable_user/<id>', views.disable_user, name="disable_user"),
    path('add_write_scope/<id>', views.add_write_scope, name="add_write_scope"),
    path('delete_write_scope/<id>/<scope>', views.delete_write_scope, name="delete_write_scope"),
    path('add_read_scope/<id>', views.add_read_scope, name="add_read_scope"),
    path('delete_read_scope/<id>/<scope>', views.delete_read_scope, name="delete_read_scope"),
    path('enable_admin/<id>', views.enable_admin, name="enable_admin"),
    path('disable_admin/<id>', views.disable_admin, name="disable_admin"),
    path('community', views.community, name="community"),
    path('ai', views.ai, name="ai"),
    path('notifications/', views.notifications, name="notifications"),
    path('notification_read/', views.notification_read_id, name="notification_read_id"),
    path('notification_read/<id>', views.notification_read_id, name="notification_read_id_sub"),
    path('search', views.search, name="search"),
    path('add_ai_task', views.add_ai_task, name="add_ai_task"),
    path('complate_ai_task', views.complate_ai_task, name="complate_ai_task"),

    path('settings/dark_mode', views.settings_dark_mode, name="settings_dark_mode"),
    path('settings/light_mode', views.settings_light_mode, name="settings_light_mode"), 

    path('', RedirectView.as_view(url='/home', permanent=False), name='index')

]
