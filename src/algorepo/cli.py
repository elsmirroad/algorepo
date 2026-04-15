import typer
from click import Command, Context, UsageError
from rich.console import Console
from typer.core import TyperGroup

from algorepo.exceptions import AlgorepoError, ConfigError, SolutionsListError
from algorepo.main import Algorepo
from algorepo.utils import format_list, format_result


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
            client = Algorepo()
            result = client.download_problem(url=url, language=language, open_editor=not no_editor)
        output = format_result(
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
def config():
    """Open the configuration file in an editor."""
    try:
        with console.status("[bold green]Loading config...[/bold green]", spinner="dots"):
            client = Algorepo()
        client.open_in_editor(client.config_path)
    except ConfigError as e:
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
