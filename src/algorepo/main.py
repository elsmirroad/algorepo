import os
import subprocess
from pathlib import Path
from typing import NamedTuple

from algorepo.config import Config
from algorepo.exceptions import ConfigurationError
from algorepo.languages import SNIPPETS, select_language
from algorepo.languages.languages import Language
from algorepo.models import Problem
from algorepo.platforms.base import Platform
from algorepo.utils import (
    NAMES,
    get_list,
    get_platform,
    get_platform_list,
    render_solution_file,
    validate_url,
)


class DownloadResult(NamedTuple):
    filepath: Path
    problem: Problem
    language: Language


class Algorepo:
    def __init__(self):
        self.config_path = Path("config.yaml")
        self.config = Config.from_yaml(self.config_path)

    def download_problem(
        self,
        url: str,
        language: str | None = None,
        open_editor: bool = True,
    ) -> DownloadResult:
        platform_name: str = validate_url(url)

        platform: Platform = get_platform(name=platform_name, config=self.config)
        raw: dict[str, str] = platform.fetch(url)
        problem: Problem = platform.parse(raw, url)

        lang: Language = select_language(
            available=problem.available_languages,
            platform=platform_name,
            priority=self.config.language_priority,
            preferred=language,
        )

        content: str = render_solution_file(
            problem=problem,
            language=lang,
            code=problem.code_snippets.get(lang.platform_ids[platform_name]) or SNIPPETS[lang.name],
        )
        filepath: Path = self._save(problem=problem, lang=lang, content=content)

        result: DownloadResult = DownloadResult(
            filepath=filepath,
            problem=problem,
            language=lang,
        )

        return result

    def open_in_editor(self, filepath: Path) -> None:
        """Open file in configured editor"""
        try:
            subprocess.run([self.config.editor, str(filepath)])
        except FileNotFoundError:
            raise ConfigurationError(reason="editor", editor=self.config.editor)
        except PermissionError:
            raise ConfigurationError(reason="permission")

    def _save(self, problem: Problem, lang: Language, content: str) -> Path:
        filename: str = self.get_filename(
            platform=problem.platform, problem_id=problem.problem_id, problem_title=problem.title
        )
        extension: str = lang.extension
        platform: str = NAMES.get(problem.platform, problem.platform)
        path: Path = self.config.solutions_dir / platform / f"{filename}{extension}"
        path.parent.mkdir(parents=True, exist_ok=True)
        os.chdir(path.parent)

        with open(path, "w", encoding="UTF-8") as file:
            file.write(content)

        return path

    def get_info(self, platform: str | None = None) -> dict:
        """Get aggregated info for all (or Platform) solutions in Repo"""

        if platform:
            platform = NAMES[platform]
            start_dir = self.config.solutions_dir / platform
            return get_platform_list(start_dir)

        start_dir: Path = self.config.solutions_dir
        solutions: dict[str, str] = {
            k: v for k, v in get_list(start_dir).items() if k in NAMES.values()
        }

        return solutions

    def get_filename(self, platform: str, problem_id: str, problem_title: str) -> str:
        if platform == "leetcode":
            return f"{problem_id}. {problem_title}"
        elif platform == "codewars":
            return f"{problem_title} | {problem_id}"
        else:
            return f"{problem_title}"
