import json

import pytest

from algorepo.config import Config
from algorepo.platforms.leetcode import LeetCodePlatform


@pytest.fixture
def leetcode_config():
    return Config()

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
