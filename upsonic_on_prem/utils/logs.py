import rich
from upsonic_on_prem.utils.configs import *

def successfully(message):
    rich.print(f"[bold green]✔[/bold green] {message}")

def failed(message):
    rich.print(f"[bold red]✘[/bold red] {message}")

def info(message):
    rich.print(f"[bold blue]ℹ[/bold blue] {message}")

def warning(message):
    rich.print(f"[bold yellow]⚠[/bold yellow] {message}")


def debug(message):
    if debugging:
        rich.print(f"[bold gray]-[/bold gray] {message}")

    else:
        pass
