import os
import subprocess
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path

from algorepo.config import Config
from algorepo.exceptions import TesterError, TesterErrorReason
from algorepo.models import FunctionSignature, TestCase
from algorepo.platforms.base import Platform
from algorepo.utils.tester import (
    parse_signature,
    save_test_cases_to_json,
)


class BaseRunner(ABC):
    def __init__(self, config: Config):
        self.config = config

    @abstractmethod
    def run(self, filepath: Path, description: str, platform: Platform) -> None:
        """Execute tests for the given solution file."""
        pass

    def _get_test_data(self, description: str, platform: Platform) -> tuple[list[TestCase], Path]:
        """Helper to parse and save test cases to a temporary JSON file."""
        test_cases: list[TestCase] = platform.extract_test_cases(text=description)
        # Create a temp file that won't be deleted immediately so the runner can read it
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        json_path = Path(path)
        save_test_cases_to_json(test_cases=test_cases, path=json_path)
        return test_cases, json_path

    def _get_signature(
        self, filepath: Path, description: str, language: str
    ) -> FunctionSignature | None:
        """Helper to find function signature in description or file."""
        sig = parse_signature(text=description, language=language)
        if not sig:
            content = filepath.read_text(encoding="utf-8")
            sig = parse_signature(text=content, language=language)
        return sig

    def _execute(self, cmd: list[str], cwd: Path | None = None) -> None:
        """Common method to run subprocess."""
        try:
            subprocess.run(cmd, check=True, cwd=cwd)
        except subprocess.CalledProcessError as e:
            raise TesterError(
                reason=TesterErrorReason.RUNTIME_ERROR,
                language="Internal",
                details=str(e),
            )
        except FileNotFoundError as e:
            raise TesterError(
                reason=TesterErrorReason.RUNTIME_ERROR,
                language="Internal",
                details=f"Command not found: {e.filename}",
            )
