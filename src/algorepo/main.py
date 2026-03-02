import os
import subprocess
from pathlib import Path
from typing import NamedTuple

from algorepo.config import Config
from algorepo.languages import select_language
from algorepo.languages.languages import Language
from algorepo.models import Problem
from algorepo.renderer import render_solution_file
from algorepo.utils import NAMES, get_list, get_platform, validate_url
from algorepo.utils.agregator import get_platform_list


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
        platform_name = validate_url(url)

        platform = get_platform(name=platform_name, config=self.config)
        raw = platform.fetch(url)
        problem = platform.parse(raw, url)

        lang = select_language(
            available=list(problem.code_snippets.keys()),
            platform=platform_name,
            priority=self.config.language_priority,
            preferred=language,
        )

        content = render_solution_file(
            problem=problem,
            language=lang,
            code=problem.code_snippets[lang.platform_ids[platform_name]],
        )
        filepath = self._save(problem=problem, lang=lang, content=content)

        result = DownloadResult(
            filepath=filepath,
            problem=problem,
            language=lang,
        )

        return result

    def open_in_editor(self, filepath: Path) -> None:
        subprocess.run([self.config.editor, str(filepath)])

    def _save(self, problem: Problem, lang: Language, content: str) -> Path:
        filename = f"{problem.problem_id}. {problem.title}"
        extension = lang.extension
        platform = NAMES.get(problem.platform, problem.platform)
        path = self.config.solutions_dir / platform / f"{filename}{extension}"
        path.parent.mkdir(parents=True, exist_ok=True)
        os.chdir(path.parent)

        with open(path, "w", encoding="UTF-8") as file:
            file.write(content)

        return path

    def get_info(self, platform: str | None = None) -> dict:
        """Get agregated info for all (or Platform) solutions in Repo"""

        if platform:
            platform = NAMES[platform]
            start_dir = self.config.solutions_dir / platform
            return get_platform_list(start_dir)

        start_dir = self.config.solutions_dir
        solutions = {k: v for k, v in get_list(start_dir).items() if k in NAMES.values()}

        return solutions
