from urllib.parse import urlparse

import httpx
from pydantic import HttpUrl

from algorepo.exceptions import NetworkError, ProblemNotFoundError
from algorepo.models import Problem
from algorepo.platforms.base import Platform

QUERY = """
  query questionData($titleSlug: String!) {
      question(titleSlug: $titleSlug) {
          questionId
          title
          difficulty
          content
          codeSnippets {
            langSlug
            code
            }
          sampleTestCase
      }
  }
  """


class LeetCodePlatform(Platform):
    GRAPHQL_URL = "https://leetcode.com/graphql"

    def __init__(self) -> None:
        pass

    def fetch(self, url: str) -> dict:
        slug = self._extract_slug(url)
        try:
            response = httpx.post(
                self.GRAPHQL_URL,
                json={
                    "query": QUERY,
                    "variables": {"titleSlug":slug}
                }
            )
            response.raise_for_status()
        except httpx.HTTPError as e:
            raise NetworkError(str(e)) from e
        return response.json()

    def parse(self, raw: dict, url: str) -> Problem:
        question = raw.get("data", {}).get("question")
        if not question:
            raise ProblemNotFoundError(f"Problem was not found: {url}")
        return Problem(
            id=question["questionId"],
            title=question["title"],
            platform="leetcode",
            difficulty=question["difficulty"],
            description=question["content"],
            url=HttpUrl(url),
            code_snippets={s["langSlug"]: s["code"] for s in question["codeSnippets"]},
            sample_test_case=question.get("sampleTestCase"),
        )

    @staticmethod
    def _extract_slug(url: str) -> str:
        """Extract slug from link"""
        extracted = urlparse(url)
        return extracted.path.split('/')[2]
