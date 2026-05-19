from pathlib import Path

import typer
from click import Command, Context, UsageError
from rich.console import Console
from typer.core import TyperGroup

from algorepo.exceptions import AlgorepoError, ConfigurationError, SolutionsListError
from algorepo.main import Algorepo, DownloadResult
from algorepo.utils import format_list, format_result
from algorepo.utils.workspace import get_problem_path


class DefaultCommandGroup(TyperGroup):
    def resolve_command(
        self, ctx: Context, args: list[str]
    ) -> tuple[str | None, Command | None, list[str]]:
        try:
            return super().resolve_command(ctx, args)
        except UsageError:
            if args[0].startswith("http"):
                args.insert(0, "download")
                return super().resolve_command(ctx, args)
            else:
                raise typer.Exit(1)


app = typer.Typer(
    help="CLI utility for parsing algorithmic problems",
    cls=DefaultCommandGroup,
    no_args_is_help=True,
)
console = Console()


@app.command()
def download(
    url: str = typer.Argument(..., help="URL problem (LeetCode // Codewars)"),
    language: str | None = typer.Option(None, "--lang", "-l", help="Solution language"),
    no_editor: bool = typer.Option(False, "--no-editor", help="Do not open editor"),
):
    """Download the problem and create a solution file."""
    try:
        with console.status("[bold green]Downloading problem...[/bold green]", spinner="dots"):
            client: Algorepo = Algorepo()
            result: DownloadResult = client.download_problem(
                url=url, language=language, open_editor=not no_editor
            )
        output: str = format_result(
            problem_id=result.problem.problem_id,
            problem=result.problem.title,
            difficulty=result.problem.difficulty,
            language=result.language.name,
            filepath=str(result.filepath),
        )
        console.print(output)

        if not no_editor:
            client.open_in_editor(result.filepath)

    except AlgorepoError as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def test(
    problem: str = typer.Argument(..., help="Problem ID, name, or path to the solution file"),
    platform: str = typer.Option(
        "leetcode", "--platform", "-p", help="Platform name (default: leetcode)"
    ),
):
    """Run tests for a solution file."""
    repo = Algorepo()

    path = Path(problem)
    if not path.exists():
        path = get_problem_path(repo.config.solutions_dir, platform, problem)

    if not path or not path.exists():
        console.print(f"[red]✗ Error:[/red] Could not find solution file for '{problem}'")
        raise typer.Exit(1)

    try:
        with console.status(f"[bold green]Running tests for {path.name}...", spinner="dots"):
            pass

        repo.test_problem(path)
    except AlgorepoError as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def config():
    """Open the configuration file in an editor."""
    try:
        with console.status("[bold green]Loading config...[/bold green]", spinner="dots"):
            client = Algorepo()
        client.open_in_editor(client.config_path)
    except ConfigurationError as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        raise typer.Exit(1)


@app.command(name="list")
def list_solutions(
    platform: str | None = typer.Option(
        None, "-p", "--platform", help="leetcode // codewars -> Get list of Solutions"
    ),
):
    """Show all downloaded solutions."""
    try:
        with console.status("[bold green]Loading config...[/bold green]", spinner="dots"):
            client = Algorepo()
        solutions_list = client.get_info(platform=platform)
        output = format_list(solutions_list)
        console.print(output)
    except SolutionsListError as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        raise typer.Exit(1)
