import json

import pytest

from algorepo.config import Config
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

    # Test typical "train" URL which includes language
    url = "https://www.codewars.com/kata/526989a410342851fe000008/train/python"
    assert platform._extract_lang(url) == "python"

    # Test standard URL without explicit language
    url = "https://www.codewars.com/kata/526989a410342851fe000008"
    assert platform._extract_lang(url) is None
