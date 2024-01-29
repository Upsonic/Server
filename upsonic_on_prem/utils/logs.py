import rich

def successfully(message):
    rich.print(f"[bold green]✔[/bold green] {message}")

def failed(message):
    rich.print(f"[bold red]✘[/bold red] {message}")