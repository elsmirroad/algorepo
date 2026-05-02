from pathlib import Path

import yaml
from pydantic import BaseModel, ValidationError, field_validator

from algorepo.exceptions import ConfigurationError


class Config(BaseModel):
    solutions_dir: Path = Path("~/Solutions").expanduser()
    language_priority: list[str] = ["Python3"]
    editor: str = "code"
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
            return cls()

        try:
            with open(path) as f:
                data = yaml.safe_load(f) or {}
        except PermissionError:
            raise ConfigurationError(reason="permission", path=str(path))
        except yaml.YAMLError:
            raise ConfigurationError(reason="invalid_format", path=str(path))
        except Exception:
            raise ConfigurationError(reason="invalid_format", path=str(path))

        try:
            return cls(**data.get("general", {}))
        except ValidationError:
            raise ConfigurationError(reason="invalid_format", path=str(path))
