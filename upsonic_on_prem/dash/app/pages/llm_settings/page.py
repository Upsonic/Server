# Page Informations
from app.pages.utils import get_current_directory_name
name = "LLM Settings"
location = get_current_directory_name()
#


from django.urls import path, include
from app import views
from dash.logs import logger
from django.shortcuts import render
from app.api_integration import API_Integration
from app import models
from django.contrib.auth.decorators import login_required






@login_required
def view(request):
    logger.debug("Hi")
    result = None

    default_ai_model = API_Integration(request.user.access_key).get_default_ai_model()

    if request.method == "POST":
        input_data = request.POST.get("model")
        result = API_Integration(request.user.access_key).change_default_ai_model(input_data)
        default_ai_model = input_data






    data = {
        "page_title": name,
        "default_ai_model": default_ai_model,
        "result": result,
    }
    return render(request, f"pages/{location}/template.html", data)








url = path(location, view, name=name)


