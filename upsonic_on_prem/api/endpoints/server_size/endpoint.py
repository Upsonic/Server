# API Informations
from upsonic_on_prem.api.utils.db import storage
from upsonic_on_prem.api.endpoints.utils import (
    get_current_directory_name,
    get_scope_name,
    request,
    app,
    jsonify,
)

url = get_current_directory_name()
auth = "admin"
scope_write_auth = False
scope_read_auth = False
#


@app.route(url, methods=["GET"])
def endpoint():
    """ """

    total_size = storage.total_size()

    return jsonify(
        {
            "status": True,
            "result": total_size,
        }
    )
