# API Informations
from upsonic_on_prem.api.endpoints.utils import app
from upsonic_on_prem.api.endpoints.utils import get_current_directory_name
from upsonic_on_prem.api.endpoints.utils import get_scope_name
from upsonic_on_prem.api.endpoints.utils import jsonify
from upsonic_on_prem.api.endpoints.utils import request
from upsonic_on_prem.api.utils.db import storage

url = get_current_directory_name()
auth = "admin"
scope_write_auth = False
scope_read_auth = False
#


@app.route(url, methods=["GET"])
def endpoint():
    """ """

    total_size = storage.total_size()

    return jsonify({
        "status": True,
        "result": total_size,
    })
