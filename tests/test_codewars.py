import json

import pytest

from algorepo.config import Config
from algorepo.exceptions import NetworkError, ProblemNotFoundError
from algorepo.platforms.codewars import CodeWarsPlatform


@pytest.fixture
def codewars_config():
    return Config()


def test_codewars_fetch(httpx_mock, codewars_config):
    with open("tests/fixtures/codewars_challenge.json") as f:
        fixture = json.load(f)

    # Mock the specific API endpoint for CodeWars
    httpx_mock.add_response(
        url="https://www.codewars.com/api/v1/code-challenges/526989a410342851fe000008", json=fixture
    )

    platform = CodeWarsPlatform(codewars_config)
    # The fetch method extracts the slug from the URL and calls the API
    raw = platform.fetch("https://www.codewars.com/kata/526989a410342851fe000008")
    assert raw["name"] == "Even or Odd"
    assert raw["id"] == "526989a410342851fe000008"


def test_codewars_parse(codewars_config):
    with open("tests/fixtures/codewars_challenge.json") as f:
        raw = json.load(f)

    platform = CodeWarsPlatform(codewars_config)
    problem = platform.parse(raw, "https://www.codewars.com/kata/526989a410342851fe000008")

    assert problem.title == "Even or Odd"
    assert problem.platform == "codewars"
    assert problem.difficulty == "8 kyu"
    assert problem.problem_id == "526989a410342851fe000008"
    assert "python" in problem.available_languages


def test_codewars_extract_lang_from_url(codewars_config):
    platform = CodeWarsPlatform(codewars_config)

    # Test action URL variants
    urls_langs = {
        "https://www.codewars.com/kata/123/train/python": "python",
        "https://www.codewars.com/kata/123/solutions/javascript": "javascript",
        "https://www.codewars.com/kata/123/discuss/cpp": "cpp",
        "https://www.codewars.com/kata/123/fork/ruby": "ruby",
        "https://www.codewars.com/kata/123/translations/java": "java",
    }
    for url, lang in urls_langs.items():
        assert platform._extract_lang(url) == lang

    # Test direct language URL
    url = "https://www.codewars.com/kata/123/csharp"
    assert platform._extract_lang(url) == "csharp"

    # Test standard URL without explicit language
    url = "https://www.codewars.com/kata/123"
    assert platform._extract_lang(url) is None


def test_codewars_extract_slug_invalid(codewars_config):
    platform = CodeWarsPlatform(codewars_config)
    with pytest.raises(ProblemNotFoundError):
        platform._extract_slug("https://www.codewars.com/users/someuser")


def test_codewars_fetch_404(httpx_mock, codewars_config):
    httpx_mock.add_response(
        url="https://www.codewars.com/api/v1/code-challenges/invalid-slug", status_code=404
    )
    platform = CodeWarsPlatform(codewars_config)

    with pytest.raises(ProblemNotFoundError):
        platform.fetch("https://www.codewars.com/kata/invalid-slug")


def test_codewars_fetch_network_error(httpx_mock, codewars_config):
    httpx_mock.add_response(
        url="https://www.codewars.com/api/v1/code-challenges/123", status_code=500
    )
    platform = CodeWarsPlatform(codewars_config)

    with pytest.raises(NetworkError):
        platform.fetch("https://www.codewars.com/kata/123")
