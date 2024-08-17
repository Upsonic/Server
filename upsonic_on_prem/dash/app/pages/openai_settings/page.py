# Page Informations
from app.pages.utils import get_current_directory_name

name = "OpenAI Settings"
location = get_current_directory_name()
#


from django.urls import path
from dash.logs import logger
from django.shortcuts import render
from app.api_integration import API_Integration
from django.contrib.auth.decorators import login_required


@login_required
def view(request):
    logger.debug("Hi")
    result = None

    default_ai_model = API_Integration(request.user.access_key).get_default_ai_model()

    if request.method == "POST":
        input_data = request.POST.get("api_key")
        result = API_Integration(request.user.access_key).change_openai_api_key(
            input_data
        )
        default_ai_model = input_data


    currently_api_key = API_Integration(request.user.access_key).view_openai_api_key()
    if currently_api_key:
        currently_api_key = currently_api_key[:10] + "..." + currently_api_key[-4:]

    data = {
        "page_title": name,
        "default_ai_model": default_ai_model,
        "result": result,
        "currently_api_key": currently_api_key,
    }
    return render(request, f"pages/{location}/template.html", data)


url = path(location, view, name=name)
