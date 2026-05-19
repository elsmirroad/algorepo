import subprocess
from pathlib import Path
from typing import NamedTuple

from algorepo.config import Config, get_config_dir
from algorepo.exceptions import (
    ConfigErrorReason,
    ConfigurationError,
    LanguageErrorReason,
    SolutionsListError,
    UnsupportedLanguageError,
)
from algorepo.languages import select_language
from algorepo.languages.languages import LANGUAGES, Language
from algorepo.models import Problem
from algorepo.platforms.base import Platform
from algorepo.testers.runners import get_runner
from algorepo.utils import (
    NAMES,
    NAMES_INV,
    format_filename,
    get_list,
    get_platform,
    get_platform_list,
    load_snippet,
    load_template,
    render_solution_file,
    validate_url,
)
from algorepo.utils.tester import extract_description
from algorepo.utils.workspace import ensure_gitignore, sync_testers


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
        language: str | None,
        open_editor: bool,
    ) -> DownloadResult:
        platform_name: str = validate_url(url=url)

        platform: Platform = get_platform(name=platform_name, config=self.config)
        raw: dict = platform.fetch(url=url)
        problem: Problem = platform.parse(raw=raw, url=url)

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
        filepath: Path = self._save(
            problem=problem, lang=lang, content=content, platform_handler=platform
        )

        result: DownloadResult = DownloadResult(
            filepath=filepath,
            problem=problem,
            language=lang,
        )

        self.initialize_workspace()

        return result

    def initialize_workspace(self) -> None:
        """Ensure .gitignore, testers, and default config are present"""
        if not self.config_path.exists():
            from algorepo.config.config import get_default_config_template

            try:
                self.config_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.config_path, "w", encoding="utf-8") as f:
                    f.write(get_default_config_template())
            except Exception as e:
                raise ConfigurationError(
                    reason=ConfigErrorReason.CREATION_FAILED,
                    path=str(self.config_path),
                    editor=None,
                    details=str(e),
                )

        ensure_gitignore(self.config.solutions_dir)
        sync_testers(self.config.solutions_dir)

    def test_problem(self, filepath: Path) -> None:
        """Run tests for solution file"""

        abs_path = filepath.resolve()
        dir_name = abs_path.parent.name
        platform_key = NAMES_INV.get(dir_name)
        if not platform_key:
            platform_key = dir_name.lower()

        try:
            platform = get_platform(name=platform_key, config=self.config)
        except (KeyError, Exception):
            from algorepo.exceptions import UnsupportedPlatformError

            raise UnsupportedPlatformError(platform_name=dir_name, supported=list(NAMES.values()))

        ext = filepath.suffix
        lang = next(
            (lang_obj for lang_obj in LANGUAGES.values() if lang_obj.extension == ext),
            None,
        )
        if not lang:
            raise UnsupportedLanguageError(
                reason=LanguageErrorReason.NOT_SUPPORTED,
                language=ext,
                supported=[lang_obj.extension for lang_obj in LANGUAGES.values()],
                available=[],
            )

        binaries = {
            "C": ["gcc"],
            "C++": ["g++"],
            "Rust": ["rustc"],
            "Go": ["go"],
            "JavaScript": ["node"],
            "TypeScript": ["node", "npx"],
            "Java": ["javac", "java"],
            "Kotlin": ["kotlinc", "java"],
        }

        required = binaries.get(lang.name, [])
        from algorepo.utils.workspace import check_binary

        missing = [b for b in required if not check_binary(name=b)]

        if missing:
            from algorepo.exceptions import DependencyError, DependencyErrorReason

            raise DependencyError(
                reason=DependencyErrorReason.MISSING_BINARY,
                language=lang.name,
                missing=missing,
            )

        description = extract_description(filepath=filepath, comment_symbol=lang.comment_symbol)

        self.initialize_workspace()

        runner = get_runner(language_name=lang.name, config=self.config)
        if runner:
            runner.run(filepath=filepath, description=description, platform=platform)
        else:
            print(f"Testing for {lang.name} is not fully implemented yet.")

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

    def _save(
        self, problem: Problem, lang: Language, content: str, platform_handler: Platform
    ) -> Path:
        filename: str = platform_handler.get_filename(problem=problem)
        filename = format_filename(name=filename)

        extension: str = lang.extension
        platform: str = NAMES.get(problem.platform, problem.platform)
        path: Path = self.config.solutions_dir / platform / f"{filename}{extension}"

        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="UTF-8") as file:
                file.write(content)
        except OSError as e:
            raise ConfigurationError(
                reason=ConfigErrorReason.PERMISSION, path=str(path), editor=None, details=str(e)
            )

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
