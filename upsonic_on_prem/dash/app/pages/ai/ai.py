from django.urls import path, include
from app import views
from dash.logs import logger
from django.shortcuts import render
from app.api_integration import API_Integration
from app import models
from django.contrib.auth.decorators import login_required


@login_required
def ai(request):
    logger.debug("Hi")
    result = None

    if request.method == "POST":
        input_data = request.POST.get("ai_input")
        result = API_Integration(request.user.access_key).ai_completion(input_data)

    the_list = models.AI_Task.objects.filter(status=False)
    tasks = []
    for task in the_list:
        if request.user.can_read(task.key):
            tasks.append(task)
    data = {
        "page_title": "AI",
        "tasks": tasks,
        "result": result,
    }
    return render(request, "pages/ai/ai.html", data)


func = ai
name = "AI"
location = "ai"




url = path(location, func, name=name)


