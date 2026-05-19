import os
import subprocess
from pathlib import Path
from typing import NamedTuple

from algorepo.config import Config, get_config_dir
from algorepo.exceptions import (
    ConfigErrorReason,
    ConfigurationError,
    SolutionsListError,
)
from algorepo.languages import select_language
from algorepo.languages.languages import Language
from algorepo.models import Problem
from algorepo.platforms.base import Platform
from algorepo.utils import (
    NAMES,
    get_list,
    get_platform,
    get_platform_list,
    load_snippet,
    load_template,
    render_solution_file,
    validate_url,
)


class DownloadResult(NamedTuple):
    filepath: Path
    problem: Problem
    language: Language


class Algorepo:
    def __init__(self):
        self.config_path = get_config_dir() / "config.yaml"
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
            preferred=problem.preffered_lang or language,
        )

        template = load_template(language_name=lang.name, config=self.config)
        snippet = load_snippet(
            language_name=lang.name, extension=lang.extension, config=self.config
        )

        platform_code = problem.code_snippets.get(lang.platform_ids[platform_name])
        final_code = platform_code if platform_code else snippet

        content: str = render_solution_file(
            problem=problem,
            language=lang,
            code=final_code,
            template=template,
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
            raise ConfigurationError(
                reason=ConfigErrorReason.EDITOR, path=None, editor=self.config.editor
            )
        except PermissionError:
            raise ConfigurationError(reason=ConfigErrorReason.PERMISSION, path=None, editor=None)

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
            platform_name = NAMES[platform]
            start_dir = self.config.solutions_dir / platform_name
        else:
            start_dir = self.config.solutions_dir

        try:
            if platform:
                return get_platform_list(start_dir)
            return {k: v for k, v in get_list(start_dir).items() if k in NAMES.values()}
        except FileNotFoundError:
            raise SolutionsListError(path=str(start_dir))

    def get_filename(self, platform: str, problem_id: str, problem_title: str) -> str:
        if platform == "leetcode":
            return f"{problem_id}. {problem_title}"
        elif platform == "codewars":
            return f"{problem_title} | {problem_id}"
        else:
            return f"{problem_title}"
