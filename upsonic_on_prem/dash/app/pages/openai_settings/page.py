# Page Informations
from app.pages.utils import get_current_directory_name

name = "OpenAI Settings"
location = get_current_directory_name()
hiden = True
#


from django.urls import path
from dash.logs import logger
from django.shortcuts import render
from django.shortcuts import redirect
from app.api_integration import API_Integration
from django.contrib.auth.decorators import login_required


@login_required
def view(request):

    result = None



    if request.method == "POST":

        api_key_ = request.POST.get("api_key")



        if api_key_:
            API_Integration(request.user.access_key).change_openai_api_key(api_key_)
            result = "OpenAI Key Updated"




    openai = API_Integration(request.user.access_key).view_openai()
    currently_api_key = API_Integration(request.user.access_key).view_openai_api_key()


    if currently_api_key:
        the_length = len(currently_api_key)
        currently_api_key = "*" * the_length

    data = {
        "page_title": name,

        "result": result,
        "currently_api_key": currently_api_key,
        "openai": openai
    }
    return redirect(to="AI Providers")


url = path(location, view, name=name)
