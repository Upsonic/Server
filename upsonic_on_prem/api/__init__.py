from .urls import *






from waitress import serve
from flask import Flask, request, Response, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


from werkzeug.middleware.proxy_fix import ProxyFix

from upsonic_on_prem.api.utils.configs import *

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

from upsonic_on_prem.api.utils import storage

database_name_caches = []
key_name_caches = []



app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)
limiter = Limiter(get_remote_address, app=app, default_limits=rate_limit)



if infrastackai:
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor, ConsoleSpanExporter
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import (
        BatchSpanProcessor,
        ConsoleSpanExporter,
    )

    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.flask import FlaskInstrumentor

    # Creates a tracer from the global tracer provider
    tracer = trace.get_tracer("my.tracer.name")
    resource = Resource.create({"service.name": "API"})
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    # Adds span processor with the OTLP exporter to the tracer provider
    provider.add_span_processor(
        SimpleSpanProcessor(OTLPSpanExporter(endpoint="https://collector-us1-http.infrastack.ai/v1/traces", headers=(("infrastack-api-key", infrastackai_api_key),)))
    )


    tracer = trace.get_tracer(__name__)

    FlaskInstrumentor().instrument_app(app, tracer_provider=provider)





@app.route(status_url, methods=["GET"])
def status():
    return jsonify({"status": True, "result": True})





from .limit import *
from .pre_process import *

from .operations import *
