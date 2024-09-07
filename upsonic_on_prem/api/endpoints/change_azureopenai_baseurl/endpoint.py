# API Informations
from upsonic_on_prem.api.endpoints.utils import (
    get_current_directory_name,
)
from upsonic_on_prem.api.app import app
from flask import jsonify, request

url = get_current_directory_name()
name_of_endpoint = url.replace("/", "_")
auth = "admin"
scope_write_auth = False
scope_read_auth = False
method = "POST"
#


from upsonic_on_prem.api.utils.kot_db import kot_db


def endpoint():
    """ """

    azureopenai_baseurl = request.form.get("baseurl")



    result = kot_db.set("azureopenai_baseurl", azureopenai_baseurl)

    return jsonify(
        {
            "status": True,
            "result": result,
        }
    )


endpoint.__name__ = name_of_endpoint
app.route(url, methods=[method])(endpoint)
