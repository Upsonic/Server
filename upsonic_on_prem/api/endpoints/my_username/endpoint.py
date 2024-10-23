# API Informations
from upsonic_on_prem.api.endpoints.utils import get_current_directory_name
from upsonic_on_prem.api.app import app
from flask import jsonify, request

import requests
import traceback


url = get_current_directory_name()
name_of_endpoint = url.replace("/", "_")
auth = "user"
scope_write_auth = False
scope_read_auth = False
method = "GET"
#



from upsonic_on_prem.__init__ import __version__

def endpoint():
    """ """
    try:
        result = requests.post("http://localhost:3001/get_username_of_ak", data={"access_key":request.authorization.password}).json()["result"]
    except:
        traceback.print_exc()
        result = "Error"

    return jsonify(
        {
            "status": True,
            "result": result,
        }
    )


endpoint.__name__ = name_of_endpoint
app.route(url, methods=[method])(endpoint)
