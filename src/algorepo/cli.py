import typer
from rich.console import Console

app = typer.Typer(help="CLI для парсинга алгоритмических задач")
console = Console()

@app.command()
def download(
    url: str = typer.Argument(..., help="URL задачи (LeetCode или Codewars)"),
    language: str = typer.Option(None, "--lang", "-l", help="Язык решения"),
    no_editor: bool = typer.Option(False, "--no-editor", help="Не открывать редактор"),
):
    """Скачать задачу и создать файл решения."""
    ...

@app.command()
def config():
    """Открыть файл конфигурации в редакторе."""
    ...

@app.command(name="list")
def list_solutions():
    """Показать все скачанные решения."""
    ...
