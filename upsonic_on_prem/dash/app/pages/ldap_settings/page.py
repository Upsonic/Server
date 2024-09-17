# Page Informations
from app.pages.utils import get_current_directory_name

name = "LDAP Settings"
hiden = True
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
        ldap_server_ = request.POST.get("ldap_server")
        if ldap_server_:
            API_Integration(request.user.access_key).change_ldap_server(ldap_server_)
            result = "LDAP Server Updated"
        
        ldap_port_ = request.POST.get("ldap_port")
        if ldap_port_:
            API_Integration(request.user.access_key).change_ldap_port(ldap_port_)
            result = "LDAP Port Updated"

        ldap_search_ = request.POST.get("ldap_search")
        if ldap_search_:
            API_Integration(request.user.access_key).change_ldap_search(ldap_search_)
            result = "LDAP Search Updated"
        
        ldap_use_ssl_ = request.POST.get("ldap_use_ssl")
        if ldap_use_ssl_:
            API_Integration(request.user.access_key).change_ldap_use_ssl(ldap_use_ssl_)
            result = "LDAP Use SSL Updated"
        
        ldap_bind_user_ = request.POST.get("ldap_bind_user")
        if ldap_bind_user_:
            API_Integration(request.user.access_key).change_ldap_bind_user(ldap_bind_user_)
            result = "LDAP Bind User Updated"

        ldap_bind_password_ = request.POST.get("ldap_bind_password")
        if ldap_bind_password_:
            API_Integration(request.user.access_key).change_ldap_bind_password(ldap_bind_password_)
            result = "LDAP Bind Password Updated"


        username = request.POST.get("username")
        password = request.POST.get("password")
        group_name = request.POST.get("group_name")

        if username and password:

            result  = API_Integration(request.user.access_key).ldap_auth(username, password)
            if result == [None]:
                result = "Invalid Credentials"



        if username and group_name:
            result = API_Integration(request.user.access_key).ldap_check(username, group_name)
            if result == [None]:
                result = "User is not in the group"


        
        

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


    data = {
        "page_title": name,
        "currently_status": currently_status,
        "ldap_server": ldap_server,
        "ldap_port": ldap_port,
        "ldap_search": ldap_search,
        "ldap_use_ssl": ldap_use_ssl,
        "ldap_bind_user": ldap_bind_user,
        "ldap_bind_password": ldap_bind_password,
        "result": result,
    }
    return render(request, f"pages/{location}/template.html", data)


url = path(location, view, name=name)
