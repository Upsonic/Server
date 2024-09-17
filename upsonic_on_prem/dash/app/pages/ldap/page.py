# Page Informations
from app.pages.utils import get_current_directory_name

name = "LDAP"
hidden = True
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

    

        

    currently_status = API_Integration(request.user.access_key).ldap_active()

    ldap_server = API_Integration(request.user.access_key).view_ldap_server()
    ldap_port = API_Integration(request.user.access_key).view_ldap_port()
    ldap_search = API_Integration(request.user.access_key).view_ldap_search()
    ldap_use_ssl = API_Integration(request.user.access_key).view_ldap_use_ssl()

    ldap_bind_user = API_Integration(request.user.access_key).view_ldap_bind_user()
    ldap_bind_password = API_Integration(request.user.access_key).view_ldap_bind_password()



    if ldap_bind_password:
        the_length = len(ldap_bind_password)
        ldap_bind_password = "*" * the_length



    all_scopes = API_Integration(request.user.access_key).ldap_get_all_scopes()

    the_dict = {}
    for scope in all_scopes:
        the_dict[scope] = API_Integration(request.user.access_key).ldap_get_groups(scope)



    if len(the_dict) == 0:
        result = "No LDAP Permissions Found"



    data = {
        "page_title": name,
        "currently_status": currently_status,
        "ldap_server": ldap_server,
        "ldap_port": ldap_port,
        "ldap_search": ldap_search,
        "ldap_use_ssl": ldap_use_ssl,
        "ldap_bind_user": ldap_bind_user,
        "ldap_bind_password": ldap_bind_password,
        "the_permissions": the_dict,
        "result": result,
    }
    return render(request, f"pages/{location}/template.html", data)


url = path(location, view, name=name)
