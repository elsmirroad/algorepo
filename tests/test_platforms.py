import json

import pytest

from algorepo.config import Config
from algorepo.platforms.leetcode import LeetCodePlatform


@pytest.fixture
def leetcode_config():
    config = Config()
    config.leetcode_csrf_token = "mock_csrf"
    config.leetcode_session = "mock_session"
    return config


def test_leetcode_fetch(httpx_mock, leetcode_config):
    with open("tests/fixtures/leetcode_two_sum.json") as f:
        fixture = json.load(f)
    httpx_mock.add_response(json=fixture)

    platform = LeetCodePlatform(leetcode_config)
    raw = platform.fetch("https://leetcode.com/problems/two-sum/")
    assert raw["data"]["question"]["title"] == "Two Sum"


def test_leetcode_parse(leetcode_config):
    with open("tests/fixtures/leetcode_two_sum.json") as f:
        raw = json.load(f)

    platform = LeetCodePlatform(leetcode_config)
    problem = platform.parse(raw, "https://leetcode.com/problems/two-sum/")

    assert problem.title == "Two Sum"
    assert problem.platform == "leetcode"
    assert problem.difficulty == "Easy"
    assert "python3" in problem.code_snippets
    assert problem.is_premium is False


def test_leetcode_parse_premium(leetcode_config):
    """Simulate a premium task that has been successfully fetched (user has Premium)"""
    with open("tests/fixtures/leetcode_two_sum.json") as f:
        raw = json.load(f)

    raw["data"]["question"]["isPaidOnly"] = True

    platform = LeetCodePlatform(leetcode_config)
    problem = platform.parse(raw, "https://leetcode.com/problems/two-sum/")

    assert problem.title == "Two Sum"
    assert problem.is_premium is True
    assert "python3" in problem.code_snippets


def test_leetcode_parse_premium_unavailable(leetcode_config):
    """Simulate a premium task where codeSnippets are null (user does NOT have Premium)"""
    with open("tests/fixtures/leetcode_two_sum.json") as f:
        raw = json.load(f)

    raw["data"]["question"]["isPaidOnly"] = True
    raw["data"]["question"]["codeSnippets"] = None

    platform = LeetCodePlatform(leetcode_config)

    from algorepo.exceptions import ProblemErrorReason, ProblemNotFoundError
    with pytest.raises(ProblemNotFoundError) as exc:
        platform.parse(raw, "https://leetcode.com/problems/two-sum/")

    assert exc.value.reason == ProblemErrorReason.UNAVAILABLE
    assert "unavailable" in str(exc.value)
