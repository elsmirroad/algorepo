import typer
from rich.console import Console

app = typer.Typer(help="CLI utility for parsing algorithmic problems")
console = Console()

@app.command()
def download(
    url: str = typer.Argument(..., help="URL problem (LeetCode // Codewars)"),
    language: str = typer.Option(None, "--lang", "-l", help="Solution language"),
    no_editor: bool = typer.Option(False, "--no-editor", help="Do not open editor"),
):
    """Download the problem and create a solution file."""
    ...

@app.command()
def config():
    """Open the configuration file in an editor."""
    ...

@app.command(name="list")
def list_solutions():
    """Show all downloaded solutions."""
    ...
