from .urls import *






from waitress import serve
from flask import Flask, request, Response, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


from werkzeug.middleware.proxy_fix import ProxyFix

from upsonic_on_prem.utils.configs import *

if sentry:
    import sentry_sdk

    sentry_sdk.init(
        dsn="https://557ac9191a887032087e4054dda517c4@o4506678585786368.ingest.sentry.io/4506678591225856",
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        traces_sample_rate=1.0,
        # Set profiles_sample_rate to 1.0 to profile 100%
        # of sampled transactions.
        # We recommend adjusting this value in production.
        profiles_sample_rate=1.0,
    )

app = Flask(__name__)

from upsonic_on_prem.utils import storage

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
