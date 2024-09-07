# Page Informations
from app.pages.utils import get_current_directory_name

name = "Change OpenAI Status"
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

    print("Changing OpenAI status to", status)

    result = API_Integration(request.user.access_key).change_openai(
            status
        )
    
    if status == "true":

        API_Integration(request.user.access_key).change_azureopenai(
                False
            )


    return redirect(to="OpenAI Settings")


url = path(location + "/<status>", view, name=name)
