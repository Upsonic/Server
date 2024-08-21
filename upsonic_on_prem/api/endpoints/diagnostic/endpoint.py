# API Informations
from upsonic_on_prem.api.endpoints.utils import get_current_directory_name
from upsonic_on_prem.api.app import app
from flask import jsonify


url = get_current_directory_name()
name_of_endpoint = url.replace("/", "_")
auth = "admin"
scope_write_auth = False
scope_read_auth = False
method = "GET"
#


from upsonic_on_prem.api.utils.diagnostic.diagnostic import diagnostic


def endpoint():
    """ """

    result = diagnostic()

    return jsonify(
        {
            "status": True,
            "result": result,
        }
    )


endpoint.__name__ = name_of_endpoint
app.route(url, methods=[method])(endpoint)
