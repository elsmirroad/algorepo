import typer
from rich.console import Console

from algorepo.exceptions import AlgorepoError
from algorepo.main import Algorepo

app = typer.Typer(help="CLI utility for parsing algorithmic problems")
console = Console()

@app.command()
def download(
    url: str = typer.Argument(..., help="URL problem (LeetCode // Codewars)"),
    language: str = typer.Option(None, "--lang", "-l", help="Solution language"),
    no_editor: bool = typer.Option(False, "--no-editor", help="Do not open editor"),
):
    """Download the problem and create a solution file."""
    try:
        client = Algorepo()
        filepath = client.download_problem(url=url, language=language, open_editor=not no_editor)
        console.print("[green]✓[/green] ...")
        console.print(f"{filepath}")
    except AlgorepoError as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        raise typer.Exit(1)

@app.command()
def config():
    """Open the configuration file in an editor."""
    ...

@app.command(name="list")
def list_solutions():
    """Show all downloaded solutions."""
    ...
