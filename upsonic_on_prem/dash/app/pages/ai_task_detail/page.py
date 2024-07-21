# Page Informations
from app.pages.utils import get_current_directory_name
name = "AI Task Detail"
location = get_current_directory_name()
hiden = True
#



from django.urls import path, include
from app import views
from dash.logs import logger
from django.shortcuts import render
from app.api_integration import API_Integration
from app import models
from django.contrib.auth.decorators import login_required
import traceback

@login_required
def view(request, id):

    result = None



    try:
        the_object = models.AI_Task.objects.get(pk=id)

        if request.user.can_read(the_object.key):
            result = the_object.__dict__
        print(the_object)
    except:
        traceback.print_exc()

    data = {
        "page_title": name,
        "result": result,
    }
    return render(request, f"pages/{location}/template.html", data)



url = path(location+"/<id>", view, name=name)


