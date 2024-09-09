# Page Informations
from app.pages.utils import get_current_directory_name

name = "AI Providers"
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
        azureopenai_baseurl_ = request.POST.get("azureopenai_baseurl")
        azureopenai_key_ = request.POST.get("azureopenai_key")
        azureopenai_version_ = request.POST.get("azureopenai_version")

        if azureopenai_baseurl_:
            API_Integration(request.user.access_key).change_azureopenai_baseurl(azureopenai_baseurl_)
            result = "Azure OpenAI Base URL Updated"
        
        if azureopenai_key_:
            API_Integration(request.user.access_key).change_azureopenai_key(azureopenai_key_)
            result = "Azure OpenAI Key Updated"

        
        if azureopenai_version_:
            logger.info("verison")
            logger.info(azureopenai_version_)
            API_Integration(request.user.access_key).change_azureopenai_version(azureopenai_version_)
            result = "Azure OpenAI Version Updated"

    azureopenai = API_Integration(request.user.access_key).view_azureopenai()
    azureopenai_baseurl = API_Integration(request.user.access_key).view_azureopenai_baseurl()
    azureopenai_key = API_Integration(request.user.access_key).view_azureopenai_key()

    azureopenai_version = API_Integration(request.user.access_key).view_azureopenai_version()




    openai = API_Integration(request.user.access_key).view_openai()
    currently_api_key = API_Integration(request.user.access_key).view_openai_api_key()


    if currently_api_key:
        the_length = len(currently_api_key)
        currently_api_key = "*" * the_length



    if azureopenai_key:
        the_length = len(azureopenai_key)
        azureopenai_key = "*" * the_length



    if azureopenai_baseurl == None:
        azureopenai_baseurl = ""

    if azureopenai_key == None:
        azureopenai_key = ""

    if azureopenai_version == None:
        azureopenai_version = ""

    

    data = {
        "page_title": name,
        "azureopenai": azureopenai,
        "azureopenai_baseurl": azureopenai_baseurl, 
        "azureopenai_key": azureopenai_key,         
        "azureopenai_version": azureopenai_version, 
        "openai":openai,
        "currently_api_key":currently_api_key,
        "result": result,
    }
    return render(request, f"pages/{location}/template.html", data)


url = path(location, view, name=name)
