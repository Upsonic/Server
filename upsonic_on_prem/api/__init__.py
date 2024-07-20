from upsonic_on_prem.api.app import app
from .urls import *




@app.route(status_url, methods=["GET"])
def status():
    return jsonify({"status": True, "result": True})




def version_info():
    from upsonic_on_prem.api.utils.logs import successfully
    from upsonic_on_prem.__init__ import __version__
    successfully(f"Upsonic On-Prem Alive with version {str(__version__)}")


version_info()




from .pre_process import *

from .operations import *


