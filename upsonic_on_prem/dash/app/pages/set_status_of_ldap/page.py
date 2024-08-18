# Page Informations
from app.pages.utils import get_current_directory_name

name = "Change LDAP Status"
location = get_current_directory_name()
hiden = True
#


from django.urls import path
from django.shortcuts import render
from django.shortcuts import redirect
from app import models
from app.api_integration import API_Integration
from django.contrib.auth.decorators import login_required
import traceback


@login_required
def view(request, status):
    result = None

    status = status.lower()

    print("Changing LDAP status to", status)

    result = API_Integration(request.user.access_key).change_ldap_auth(
            status
        )


    return redirect(to="LDAP Settings")


url = path(location + "/<status>", view, name=name)
