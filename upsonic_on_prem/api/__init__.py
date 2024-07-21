from upsonic_on_prem.api.app import app

from .operations import *
from .pre_process import *
from .urls import *


@app.route(status_url, methods=["GET"])
def status():
    return jsonify({"status": True, "result": True})


def version_info():
    from upsonic_on_prem.__init__ import __version__
    from upsonic_on_prem.api.utils.logs import successfully

    successfully(f"Upsonic On-Prem Alive with version {str(__version__)}")


version_info()
