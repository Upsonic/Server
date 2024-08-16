# API Informations
from upsonic_on_prem.api.endpoints.utils import (
    get_current_directory_name,
    request,
    app,
    jsonify,
)

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

    default_model = request.form.get("model")

    print("default_model", default_model)

    result = kot_db.set("default_model", default_model)

    return jsonify(
        {
            "status": True,
            "result": result,
        }
    )


endpoint.__name__ = name_of_endpoint
app.route(url, methods=[method])(endpoint)
