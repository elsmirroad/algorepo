import os
import sys
from pathlib import Path

import yaml
from pydantic import BaseModel, ValidationError, field_validator
from rich.console import Console

from algorepo.exceptions import ConfigErrorReason, ConfigurationError


def get_config_dir() -> Path:
    """Return platform-specific configuration directory"""
    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming"))
        return Path(appdata) / "algorepo"
    return Path("~/.config/algorepo").expanduser()


class Config(BaseModel):
    solutions_dir: Path = Path("~/Solutions").expanduser()
    language_priority: list[str] = ["Python3"]
    editor: str = "vim"
    open_editor: bool = True
    leetcode_session: str = ""
    leetcode_csrf_token: str = ""

    @field_validator("solutions_dir", mode="before")
    @classmethod
    def expand_path(cls, v: str | Path) -> Path:
        return Path(v).expanduser()

    @classmethod
    def from_yaml(cls, path: Path) -> "Config":
        """Load config from YAML file"""
        if not path.exists():
            console = Console()
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(DEFAULT_CONFIG_TEMPLATE)
                console.print(f"[green]✓ Created default configuration template at: {path}[/green]")
            except Exception as e:
                console.print(f"[yellow]⚠ Could not create default config at {path}: {e}[/yellow]")
            return cls()

        try:
            with open(path) as f:
                data = yaml.safe_load(f) or {}
        except PermissionError:
            raise ConfigurationError(
                reason=ConfigErrorReason.PERMISSION, path=str(path), editor=None
            )
        except yaml.YAMLError:
            raise ConfigurationError(
                reason=ConfigErrorReason.INVALID_FORMAT, path=str(path), editor=None
            )
        except Exception:
            raise ConfigurationError(
                reason=ConfigErrorReason.INVALID_FORMAT, path=str(path), editor=None
            )

        try:
            return cls(**data.get("general", {}))
        except ValidationError:
            raise ConfigurationError(
                reason=ConfigErrorReason.INVALID_FORMAT, path=str(path), editor=None
            )


DEFAULT_CONFIG_TEMPLATE = """\
general:
  # The directory where your solutions will be saved
  solutions_dir: ~/Solutions

  # Your preferred languages in order of priority (e.g. Python3, C++, Java)
  language_priority:
    - Python3

  # Your preferred editor command (e.g. "nano", "vim", "nvim", "code", etc.)
  editor: vim

  # Automatically open the editor after downloading a problem
  open_editor: true

  # LeetCode credentials (optional, required only for premium/private problems)
  leetcode_session: ""
  leetcode_csrf_token: ""
"""
