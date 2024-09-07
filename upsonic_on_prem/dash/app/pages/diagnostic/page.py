# Page Informations
from app.pages.utils import get_current_directory_name

name = "Diagnostic"
location = get_current_directory_name()
#


from django.urls import path
from dash.logs import logger
from django.shortcuts import render
from app.api_integration import API_Integration
from django.contrib.auth.decorators import login_required


@login_required
def view(request):
    ai_result = None
    result = API_Integration(request.user.access_key).diagnostic()


    if request.method == "POST":

        ai_prompt_ = request.POST.get("ai_prompt")



        if ai_prompt_:
            ai_result = API_Integration(request.user.access_key).ai_completion(ai_prompt_)
            logger.info(ai_result)


        


    data = {
        "page_title": name,
        "ai_result": ai_result,
        "result": result,
    }
    return render(request, f"pages/{location}/template.html", data)


url = path(location, view, name=name)
