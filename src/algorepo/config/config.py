import os
import sys
from pathlib import Path

import yaml
from pydantic import BaseModel, ValidationError, field_validator

from algorepo.exceptions import ConfigErrorReason, ConfigurationError


def get_config_dir() -> Path:
    """Return platform-specific configuration directory"""
    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming"))
        return Path(appdata) / "algorepo"
    return Path("~/.config/algorepo").expanduser()


class Config(BaseModel):
    solutions_dir: Path = Path("~/Solutions").expanduser()
    templates_dir: Path = get_config_dir() / "templates"
    language_priority: list[str] = ["Python3"]
    editor: str = "vim"
    open_editor: bool = True
    leetcode_session: str = ""
    leetcode_csrf_token: str = ""

    @field_validator("solutions_dir", "templates_dir", mode="before")
    @classmethod
    def expand_path(cls, v: str | Path) -> Path:
        return Path(v).expanduser()

    @classmethod
    def from_yaml(cls, path: Path) -> "Config":
        """Load config from YAML file. Returns default config if file doesn't exist."""
        if not path.exists():
            return cls()

        try:
            with open(path) as f:
                data = yaml.safe_load(f) or {}
        except PermissionError:
            raise ConfigurationError(
                reason=ConfigErrorReason.PERMISSION, path=str(path), editor=None
            )
        except (yaml.YAMLError, Exception):
            raise ConfigurationError(
                reason=ConfigErrorReason.INVALID_FORMAT, path=str(path), editor=None
            )

        try:
            return cls(**data.get("general", {}))
        except ValidationError:
            raise ConfigurationError(
                reason=ConfigErrorReason.INVALID_FORMAT, path=str(path), editor=None
            )


def get_default_config_template() -> str:
    """Generate platform-aware default configuration template"""
    config_dir = get_config_dir()
    templates_dir = config_dir / "templates"

    if sys.platform == "win32":
        sol_example = "%USERPROFILE%\\Solutions"
        tmpl_desc = "If not set, uses %APPDATA%\\algorepo\\templates"
    else:
        sol_example = "~/Solutions"
        tmpl_desc = "If not set, uses ~/.config/algorepo/templates"

    return f"""\
general:
  # ===========================================================================
  # Algorepo Configuration File
  # IMPORTANT: This file contains sensitive authentication tokens.
  # It is recommended to restrict access to this file (e.g., chmod 600).
  # ===========================================================================

  # The directory where your solutions will be saved
  # Example: {sol_example}
  solutions_dir: ~/Solutions

  # Custom templates directory.
  # {tmpl_desc}
  templates_dir: {templates_dir}

  # Your preferred languages in order of priority (e.g. Python3, C++, Java)
  language_priority:
    - Python3

  # Your preferred editor command (e.g. "nano", "vim", "nvim", "code", etc.)
  editor: vim

  # Automatically open the editor after downloading a problem
  open_editor: true

  # LeetCode Authentication (REQUIRED for LeetCode)
  # Without these tokens, LeetCode's Cloudflare protection will block requests (403 Forbidden).
  # How to get them:
  # 1. Login to leetcode.com in your browser
  # 2. Open Developer Tools (F12) -> Application (or Storage) -> Cookies
  # 3. Copy the values for 'LEETCODE_SESSION' and 'csrftoken'
  leetcode_session: ""
  leetcode_csrf_token: ""
"""
