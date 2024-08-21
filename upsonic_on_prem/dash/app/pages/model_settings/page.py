# Page Informations
from app.pages.utils import get_current_directory_name

name = "Model Settings"
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

    

    if request.method == "POST":
        input_data = request.POST.get("model")
        search_model = request.POST.get("search_model")
        if search_model:
            result = API_Integration(request.user.access_key).change_default_search_model(
                search_model
            )
            result = "Search Model Changed"

        if input_data:
            result = API_Integration(request.user.access_key).change_default_ai_model(input_data)
            result = "AI Model Changed"



    default_ai_model = API_Integration(request.user.access_key).get_default_ai_model()
    default_search_model = API_Integration(request.user.access_key).get_default_search_model()

    data = {
        "page_title": name,
        "default_ai_model": default_ai_model,
        "default_search_model": default_search_model,
        "result": result,
    }
    return render(request, f"pages/{location}/template.html", data)


url = path(location, view, name=name)
