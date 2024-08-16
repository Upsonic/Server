"""
URL configuration for dash project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import path
from django.urls import include

from django.conf.urls.static import static

from dash import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("app.url")),
    path("accounts/", include("allauth.urls")),
    path("favicon.ico", lambda x: HttpResponseRedirect("/static/images/favicon.png")),
    path("", include("pwa.urls")),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
