# Page Informations
from app.pages.utils import get_current_directory_name
name = "AI Finished Tasks"
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

    if request.method == "POST":
        input_data = request.POST.get("ai_input")
        result = API_Integration(request.user.access_key).ai_completion(input_data)

    the_list = models.AI_Task.objects.filter(status=True)
    tasks = []
    for task in the_list:
        if request.user.can_read(task.key):
            tasks.append(task)


    task_len = len(tasks)

    data = {
        "page_title": name,
        "tasks": tasks,
        "task_len": task_len,
        "result": result,
    }
    return render(request, f"pages/{location}/template.html", data)



url = path(location, view, name=name)


