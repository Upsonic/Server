from upsonic_on_prem.api import app
from flask import Flask, request, Response, jsonify, redirect
import requests

from upsonic_on_prem.utils import AccessKey

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

    # Check for api_token and modify it
    api_token = request.headers.get('api_token')
    if api_token:
        # Logic to decode, modify, and re-encode the api_token goes here
        modified_api_token = 'modified_' + api_token  # Example modification

        # Forwarding the modified request
        forward_url = 'http://api.actualserver.com'  # The actual API server URL
        headers = {'api_token': modified_api_token}
        response = requests.get(forward_url, headers=headers)

        # Return the response from the API server to the client
        return Response(response.content, status=response.status_code, headers=dict(response.headers))

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
