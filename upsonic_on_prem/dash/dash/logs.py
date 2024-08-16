import logging


import os

from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

infrastackai = os.environ.get("infrastackai", "false").lower() == "true"
infrastackai_api_key = os.environ.get("infrastackai_api_key", "")

debug_mode = os.environ.get("debug", "false").lower() == "true"


logger = logging.getLogger(__name__)
if not debug_mode:
    logger.setLevel(logging.INFO)
else:
    logger.setLevel(logging.DEBUG)
logger.handlers = []


if infrastackai:
    from opentelemetry._logs import set_logger_provider
    from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
    from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
    from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
    from opentelemetry.sdk.resources import Resource

    resource = Resource.create({"service.name": "WEB"})
    # Create and set the logger provider
    logger_provider = LoggerProvider(resource=resource)
    set_logger_provider(logger_provider)

    # Create the OTLP log exporter that sends logs to configured destination
    exporter = OTLPLogExporter(
        endpoint="https://collector-us1-http.infrastack.ai/v1/logs",
        headers=(("infrastack-api-key", infrastackai_api_key),),
    )
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))

    # Attach OTLP handler to root logger
    handler = LoggingHandler(logger_provider=logger_provider)
    logger.addHandler(handler)
