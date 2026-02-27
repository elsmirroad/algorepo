from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from pydantic import HttpUrl

from algorepo.config import Config
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

    def __init__(self, config: Config) -> None:
        super().__init__(config=config)

    def fetch(self, url: str) -> dict:
        slug = self._extract_slug(url)
        try:
            response = httpx.post(
                self.GRAPHQL_URL,
                json={
                    "query": QUERY,
                    "variables": {"titleSlug":slug}
                },
                headers={
                    "Content-Type": "application/json",
                    "Referer": "https://leetcode.com",
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36", # noqa
                    "Origin": "https://leetcode.com",
                    "x-csrftoken": self.config.leetcode_csrf_token,
                },
                cookies={
                    "csrftoken": self.config.leetcode_csrf_token,
                    "LEETCODE_SESSION": self.config.leetcode_session,
                },
                timeout=30,
            )
            response.raise_for_status()
        except httpx.HTTPError as e:
            raise NetworkError(str(e)) from e
        return response.json()

    def parse(self, raw: dict, url: str) -> Problem:
        question = raw.get("data", {}).get("question")
        if not question:
            raise ProblemNotFoundError(f"Problem was not found: {url}")
        description = self._extract_description(question["content"])
        url=f"https://leetcode.com/problems/{self._extract_slug(url)}/"
        return Problem(
            id=question["questionId"],
            title=question["title"],
            platform="leetcode",
            difficulty=question["difficulty"],
            description=description,
            url=HttpUrl(url),
            code_snippets={s["langSlug"]: s["code"] for s in question["codeSnippets"]},
            sample_test_case=question.get("sampleTestCase"),
        )

    @staticmethod
    def _extract_slug(url: str) -> str:
        """Extract slug from link"""
        extracted = urlparse(url)
        return extracted.path.split('/')[2]

    @staticmethod
    def _extract_description(response_text: str) -> str:
        """Delete HTML-tags and get beauty Description"""
        description = BeautifulSoup(response_text, "lxml")
        for tag in description.find_all("sup"):
            tag.replace_with(f"^{tag.get_text()}")
        return description.get_text()
