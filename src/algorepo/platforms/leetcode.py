import re
from pathlib import Path
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from pydantic import HttpUrl

from algorepo.config import Config
from algorepo.exceptions import (
    AuthorizationError,
    NetworkError,
    NetworkErrorReason,
    ProblemErrorReason,
    ProblemNotFoundError,
)
from algorepo.models import Problem, TestCase
from algorepo.platforms.base import Platform

QUERY = """
  query questionData($titleSlug: String!) {
      question(titleSlug: $titleSlug) {
          questionFrontendId
          title
          difficulty
          isPaidOnly
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
        if not self.config.leetcode_csrf_token or not self.config.leetcode_session:
            raise AuthorizationError(platform_name="leetcode")
        slug = self._extract_slug(url=url)
        try:
            response = httpx.post(
                url=self.GRAPHQL_URL,
                json={"query": QUERY, "variables": {"titleSlug": slug}},
                headers={
                    "Content-Type": "application/json",
                    "Referer": "https://leetcode.com",
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",  # noqa
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
            raise NetworkError(
                platform_name="leetcode",
                reason=NetworkErrorReason.HTTP_ERROR,
                details=str(e),
            ) from e
        return response.json()

    def parse(self, raw: dict, url: str) -> Problem:
        question = raw.get("data", {}).get("question")
        if not question:
            raise ProblemNotFoundError(
                reason=ProblemErrorReason.NOT_FOUND, url=url, platform_name="leetcode"
            )
        is_premium = question.get("isPaidOnly", False)

        snippets = {}
        if question.get("codeSnippets"):
            snippets = {s["langSlug"]: s["code"] for s in question["codeSnippets"]}
        else:
            raise ProblemNotFoundError(
                reason=ProblemErrorReason.UNAVAILABLE, url=url, platform_name="leetcode"
            )

        description = self._extract_description(response_text=question.get("content", ""))
        url = f"https://leetcode.com/problems/{self._extract_slug(url=url)}/"

        return Problem(
            problem_id=question["questionFrontendId"],
            title=question["title"],
            platform="leetcode",
            difficulty=question["difficulty"],
            description=description,
            url=HttpUrl(url),
            code_snippets=snippets,
            sample_test_case=question.get("sampleTestCase"),
            available_languages=list(snippets.keys()),
            is_premium=is_premium,
        )

    def get_filename(self, problem: Problem) -> str:
        return f"{problem.problem_id}. {problem.title}"

    def extract_test_cases(self, text: str) -> list[TestCase]:
        """
        Parses LeetCode-style description to extract test cases.
        """
        tests: list[TestCase] = []
        p, t = "", 0

        def split_vars(s: str, prepend: str = ", ") -> list[str]:
            out = []
            if m := re.split(r"\, [a-zA-Z_]+\d* =\s*", prepend + s):
                for i in range(len(m)):
                    if m[i]:
                        out.append(m[i].strip())
            return out

        lines = text.splitlines()
        for s in lines:
            s = s.strip()
            s = re.sub(r"^(#|//|--)\s*", "", s)

            if s.startswith("Input:"):
                t = 1
                tests.append(TestCase(inputs=[], expected=""))
                p = s[6:].strip()
            elif s.startswith("Output:"):
                if tests:
                    tests[-1].inputs = split_vars(p)
                p, t = s[7:].strip(), 2
            elif t == 2 and (
                s == ""
                or any(
                    s.startswith(marker)
                    for marker in ("Example", "Explanation", "Note", "Constraints", "Follow-up")
                )
            ):
                if tests:
                    tests[-1].expected = p.strip()
                p, t = "", 0
            elif t != 0:
                p += " " + s

        if t == 2 and tests:
            tests[-1].expected = p.strip()

        return tests

    def get_tester_dir(self, language_name: str) -> Path:
        """Returns the directory containing tester libraries for LeetCode."""
        norm_name = language_name.lower().replace("++", "pp").replace("#", "sharp")
        return self.config.solutions_dir / "testers" / "leetcode" / norm_name

    @staticmethod
    def _extract_slug(url: str) -> str:
        """Extract slug from link"""
        path = urlparse(url).path.strip("/")
        parts = path.split("/")
        try:
            idx = parts.index("problems")
            if idx + 1 < len(parts):
                return parts[idx + 1]
            return parts[idx]
        except (ValueError, IndexError):
            if len(parts) >= 2:
                return parts[1]
            raise ProblemNotFoundError(
                reason=ProblemErrorReason.NOT_FOUND, url=url, platform_name="leetcode"
            )

    @staticmethod
    def _extract_description(response_text: str) -> str:
        """Delete HTML-tags and get beauty Description"""
        description = BeautifulSoup(response_text, "lxml")
        for tag in description.find_all("sup"):
            tag.replace_with(f"^{tag.get_text()}")
        return description.get_text()
