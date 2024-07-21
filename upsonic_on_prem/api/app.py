from flask import Flask, Response, jsonify, request
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from waitress import serve
from werkzeug.middleware.proxy_fix import ProxyFix

from upsonic_on_prem.api.utils import storage
from upsonic_on_prem.api.utils.configs import *

from .tracer import provider

if sentry:
    import sentry_sdk

    sentry_sdk.init(
        dsn=sentry_flask_key,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        traces_sample_rate=1.0,
        # Set profiles_sample_rate to 1.0 to profile 100%
        # of sampled transactions.
        # We recommend adjusting this value in production.
        profiles_sample_rate=1.0,
    )

app = Flask(__name__)


database_name_caches = []
key_name_caches = []


app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)


FlaskInstrumentor().instrument_app(app, tracer_provider=provider)
