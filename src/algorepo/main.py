import os
import subprocess
from pathlib import Path

from algorepo.config import Config
from algorepo.languages import select_language
from algorepo.languages.languages import Language
from algorepo.models import Problem
from algorepo.renderer import render_solution_file
from algorepo.utils.validator import NAMES, get_platform, validate_url


class Algorepo:

    def __init__(self):
        config_path = Path("config.yaml")
        self.config = Config.from_yaml(config_path)

    def download_problem(
        self,
        url: str,
        language: str | None = None,
        open_editor: bool = True,
    ) -> Path:
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
            code=problem.code_snippets[
                lang.platform_ids[platform_name]])
        filepath = self._save(problem=problem, lang=lang, content=content)

        if open_editor and self.config.open_editor:
            subprocess.run([self.config.editor, str(filepath)])

        return filepath


    def _save(self, problem: Problem, lang: Language, content: str):
        filename = f"{problem.id}. {problem.title}"
        extension = lang.extension
        platform = NAMES.get(problem.platform, problem.platform)
        path = self.config.solutions_dir / platform / f"{filename}{extension}"
        path.parent.mkdir(parents=True, exist_ok=True)
        os.chdir(path.parent)

        with open(path, "w", encoding="UTF-8") as file:
            file.write(content)

        return path

