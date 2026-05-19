from abc import ABC, abstractmethod
from pathlib import Path

from algorepo.config import Config
from algorepo.models import Problem, TestCase


class Platform(ABC):
    def __init__(self, config: Config) -> None:
        self.config = config

    @abstractmethod
    def fetch(self, url: str) -> dict:
        """Network request
        Input: URL adress form request
        Output: Raw platform data"""

    @abstractmethod
    def parse(self, raw: dict, url: str) -> Problem:
        """Problem parser
        Input: Raw problem data
        Return: Ready to solve Problem
        """

    @abstractmethod
    def get_filename(self, problem: Problem) -> str:
        """Returns the default filename for the problem on this platform."""

    @abstractmethod
    def extract_test_cases(self, text: str) -> list[TestCase]:
        """Extracts test cases from the problem description."""

    @abstractmethod
    def get_tester_dir(self, language_name: str) -> Path:
        """Returns the directory containing tester libraries for this platform and language."""
