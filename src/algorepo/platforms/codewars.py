from urllib.parse import urlparse

import httpx
from pydantic import HttpUrl

from algorepo.config import Config
from algorepo.exceptions import (
    NetworkError,
    NetworkErrorReason,
    ProblemErrorReason,
    ProblemNotFoundError,
)
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
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ProblemNotFoundError(
                    reason=ProblemErrorReason.NOT_FOUND, url=url, platform_name="codewars"
                ) from e
            raise NetworkError(
                platform_name="codewars",
                reason=NetworkErrorReason.HTTP_ERROR,
                details=str(e),
            ) from e
        except httpx.HTTPError as e:
            raise NetworkError(
                platform_name="codewars",
                reason=NetworkErrorReason.HTTP_ERROR,
                details=str(e),
            ) from e
        return response.json()

    def parse(self, raw: dict, url: str) -> Problem:
        if not raw:
            raise ProblemNotFoundError(
                reason=ProblemErrorReason.NOT_FOUND, url=url, platform_name="codewars"
            )

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
        parts = urlparse(url).path.strip("/").split("/")
        if len(parts) < 2 or parts[0] != "kata":
            raise ProblemNotFoundError(
                reason=ProblemErrorReason.NOT_FOUND, url=url, platform_name="codewars"
            )
        return parts[1]

    @staticmethod
    def _extract_lang(url: str) -> str | None:
        """Extract language from link if present"""
        parts = urlparse(url).path.strip("/").split("/")

        # Known actions keywords
        for keyword in ("train", "solutions", "discuss", "fork", "translations"):
            try:
                idx = parts.index(keyword)
                if idx + 1 < len(parts):
                    return parts[idx + 1]
            except ValueError:
                continue

        if len(parts) == 3 and parts[0] == "kata":
            return parts[2]

        return None
