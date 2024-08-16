import rich
from upsonic_on_prem.api.utils.configs import *


import logging


logger = logging.getLogger(__name__)
if not debugging:
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

    resource = Resource.create({"service.name": "API"})
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


def successfully(message):
    rich.print(f"[bold green]✔[/bold green] {message}")
    logger.info(f"✔ {message}")


def failed(message):
    rich.print(f"[bold red]✘[/bold red] {message}")
    logger.error(f"✘ {message}")


def info(message):
    rich.print(f"[bold blue]ℹ[/bold blue] {message}")
    logger.info(f"ℹ {message}")


def warning(message):
    rich.print(f"[bold yellow]⚠[/bold yellow] {message}")
    logger.warning(f"⚠ {message}")


def debug(message):
    if debugging:
        rich.print(f"[bold gray]-[/bold gray] {message}")
        logger.debug(f"- {message}")

    else:
        pass
