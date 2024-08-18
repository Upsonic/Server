# Page Informations
from app.pages.utils import get_current_directory_name

name = "LDAP Settings"
location = get_current_directory_name()
#


from django.urls import path
from dash.logs import logger
from django.shortcuts import render
from app.api_integration import API_Integration
from django.contrib.auth.decorators import login_required


@login_required
def view(request):

    result = None

    

    if request.method == "POST":
        status = request.POST.get("status")
        result = API_Integration(request.user.access_key).change_ldap_auth(
            status
        )

    currently_status = API_Integration(request.user.access_key).ldap_active()

    data = {
        "page_title": name,
        "currently_status": currently_status,
        "result": result,
    }
    return render(request, f"pages/{location}/template.html", data)


url = path(location, view, name=name)
