from pathlib import Path

import yaml
from pydantic import BaseModel, field_validator


class Config(BaseModel):
    solutions_dir: Path = Path("~/Solutions").expanduser()
    language_priority: list[str] = ["Python3"]
    editor: str = "code"
    open_editor: bool = True

    @field_validator("solutions_dir", mode="before")
    @classmethod
    def expand_path(cls, v: str | Path) -> Path:
        return Path(v).expanduser()

    @classmethod
    def from_yaml(cls, path: Path) -> "Config":
        if not path.exists():
            return cls()
        with open(path) as f:
            data = yaml.safe_load(f) or {}
        return cls(**data.get("general", {}))
