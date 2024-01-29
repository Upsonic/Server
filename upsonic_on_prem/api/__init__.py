from .urls import *







from waitress import serve
from flask import Flask, request, Response, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


from werkzeug.middleware.proxy_fix import ProxyFix
app = Flask(__name__)



from upsonic_on_prem.utils.configs import *

database_name_caches = []
key_name_caches = []



app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)
limiter = Limiter(get_remote_address, app=app, default_limits=rate_limit)


@app.route(status_url, methods=["GET"])
def status():
    return jsonify(True)





from .limit import *
from .pre_process import *

from .operations import *
