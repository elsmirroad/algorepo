import string
from importlib.resources import files

from algorepo.config import Config


def load_template(language_name: str, config: Config) -> string.Template:
    """Load a Layout template (structure of the file)"""

    # User specific Layout
    user_path = config.templates_dir / f"{language_name}.txt"
    if user_path.exists():
        return string.Template(user_path.read_text(encoding="utf-8"))

    # User default Layout
    user_default = config.templates_dir / "default.txt"
    if user_default.exists():
        return string.Template(user_default.read_text(encoding="utf-8"))

    # Internal specific Layout
    internal_templates = files("algorepo.templates")
    internal_path = internal_templates.joinpath(f"{language_name}.txt")
    if internal_path.is_file():
        return string.Template(internal_path.read_text(encoding="utf-8"))

    # Internal default Layout
    internal_default = internal_templates.joinpath("default.txt")
    return string.Template(internal_default.read_text(encoding="utf-8"))


def load_snippet(language_name: str, extension: str, config: Config) -> str:
    """Load a Code Snippet (boilerplate) by priority (USER // Internal)"""

    filename = f"{language_name}{extension}"

    # User snippet
    user_path = config.templates_dir / filename
    if user_path.exists():
        return user_path.read_text(encoding="utf-8")

    # Internal snippet
    internal_templates = files("algorepo.templates")
    internal_path = internal_templates.joinpath(filename)
    if internal_path.is_file():
        return internal_path.read_text(encoding="utf-8")

    return ""
