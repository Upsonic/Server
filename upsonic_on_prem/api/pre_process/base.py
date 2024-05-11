from upsonic_on_prem.api import app
from flask import Flask, request, Response, jsonify

from upsonic_on_prem.api.utils import AccessKey

from upsonic_on_prem.api.urls import *

from upsonic_on_prem.api.pre_process.admin import *

from upsonic_on_prem.api.pre_process.user import *


@app.before_request
def check():
    the_endpoint = request.endpoint
    if request.endpoint == None:
        the_endpoint = ""
    endpoint = "/" + the_endpoint

    if endpoint == status_url:
        return

    auth = request.authorization
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
        if not (endpoint in user_urs):
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
        return Response(
            "You don't have right to access this URL.\n"
            "You have to login with proper credentials",
            400,
            {"WWW-Authenticate": 'Basic realm="Login Required"'},
        )
