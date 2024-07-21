from upsonic_on_prem.api import app
from flask import Flask, request, Response, jsonify

from upsonic_on_prem.api.utils import AccessKey

from upsonic_on_prem.api.urls import *

from upsonic_on_prem.api.pre_process.admin import *

from upsonic_on_prem.api.pre_process.user import *
from upsonic_on_prem.api.tracer import tracer,  Status, StatusCode
from upsonic_on_prem.api.utils.logs import warning

@app.before_request
def check():
    the_endpoint = request.endpoint
    if request.endpoint == None:
        the_endpoint = ""
    endpoint = "/" + the_endpoint

    if endpoint == status_url:
        return



    


    auth = request.authorization

    the_access_key = None
    if "Authorization" in request.headers:
        if "Bearer " in request.headers.get("Authorization"):
            the_access_key = AccessKey(request.headers.get("Authorization").split(" ")[1])
            

    try:
        the_datas = request.json if request.method in ['POST', 'PUT'] else request.args
        if "model" in the_datas:
            if "**" in the_datas["model"]:
                the_access_key = AccessKey(request.json["model"].split("**")[1])
                request.json["model"] = request.json["model"].split("**")[0]
                print("endpoint", endpoint)
    except:
        pass
            
    

    if not the_access_key:
        if not auth:
            return Response(
                "Could not verify your access level for that URL. Make basic auth.\n"
                "You have to login with proper credentials",
                401,
                {"WWW-Authenticate": 'Basic realm="Login Required"'},
            )        
        the_access_key = AccessKey(auth.password)

    if not the_access_key.is_enable:
        return Response(
            "You don't have register to access this URL.\n"
            "You have to login with proper credentials",
            403,
            {"WWW-Authenticate": 'Basic realm="Login Required"'},
        )

    if not the_access_key.is_admin:
        if not (endpoint in user_urls):
            print("endpoint", endpoint)
            print(request.endpoint)
            return Response(
                "You don't have permission to access this URL.\n"
                "You have to login with proper credentials",
                403,
                {"WWW-Authenticate": 'Basic realm="Login Required"'},
            )

    pre_processor = None

    if the_access_key.is_admin:
        pre_processor = admin_pre_process
    else:
        pre_processor = user_pre_process

    if not pre_processor(the_access_key, request):
        warning(f"Access denied for {endpoint}")
        return Response(
            "You don't have right to access this URL.\n"
            "You have to login with proper credentials",
            400,
            {"WWW-Authenticate": 'Basic realm="Login Required"'},
        )
