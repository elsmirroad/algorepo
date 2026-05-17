from urllib.parse import urlparse

import httpx
from pydantic import HttpUrl

from algorepo.config import Config
from algorepo.exceptions import NetworkError, ProblemNotFoundError
from algorepo.languages import SNIPPETS
from algorepo.models import Problem
from algorepo.platforms.base import Platform


class CodeWarsPlatform(Platform):
    REST_URL = "https://www.codewars.com/api/v1/code-challenges"

    def __init__(self, config: Config) -> None:
        super().__init__(config=config)

    def fetch(self, url: str) -> dict:
        slug = self._extract_slug(url)
        try:
            response = httpx.get(
                url=f"{self.REST_URL}/{slug}",
            )
            response.raise_for_status()
        except httpx.HTTPError as e:
            raise NetworkError(str(e)) from e
        return response.json()

    def parse(self, raw: dict, url: str) -> Problem:
        if not raw:
            raise ProblemNotFoundError(f"Problem was not found: {url}")

        language = self._extract_lang(url)
        return Problem(
            problem_id=raw["id"],
            title=raw["name"],
            platform="codewars",
            difficulty=raw["rank"]["name"],
            description=raw["description"],
            url=HttpUrl(url),
            preffered_lang=language if language else None,
            code_snippets=SNIPPETS,  # Custom Snippets
            available_languages=raw["languages"],
        )

    @staticmethod
    def _extract_slug(url: str) -> str:
        """Extract slug from link"""
        extracted = urlparse(url)
        return extracted.path.split("/")[2]

    @staticmethod
    def _extract_lang(url: str) -> str | None:
        """Extract language from link if present"""
        parts = urlparse(url).path.strip("/").split("/")
        try:
            train_index = parts.index("train")
            if train_index + 1 < len(parts):
                return parts[train_index + 1]
        except ValueError:
            return None
        return None
