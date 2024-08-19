# Page Informations
from app.pages.utils import get_current_directory_name

name = "LDAP Permissions"
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
        scope_name_add = request.POST.get("scope_add")
        scope_name_remove = request.POST.get("scope_remove")

        group_name = request.POST.get("group_name")

        if scope_name_add and group_name:
            API_Integration(request.user.access_key).ldap_add_permission(scope_name_add, group_name)
            result = "Group Added"
        
        if scope_name_remove and group_name:
            API_Integration(request.user.access_key).ldap_remove_permission(scope_name_remove, group_name)
            result = "Group Removed"
        



        
        

    all_scopes = API_Integration(request.user.access_key).ldap_get_all_scopes()

    the_dict = {}
    for scope in all_scopes:
        the_dict[scope] = API_Integration(request.user.access_key).ldap_get_groups(scope)



    if len(the_dict) == 0:
        result = "No LDAP Permissions Found"


    data = {
        "page_title": name,
        "the_permissions": the_dict,
        "result": result,
    }
    return render(request, f"pages/{location}/template.html", data)


url = path(location, view, name=name)
