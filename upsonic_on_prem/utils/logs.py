import rich
from upsonic_on_prem.utils.configs import *


from logtail import LogtailHandler
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.handlers = []

if betterstack:
    print("Betterstack is enabled")
    handler = LogtailHandler(source_token=betterstack_flask_key)
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
