import pytest

from algorepo.exceptions import UnsupportedLanguageError
from algorepo.languages import select_language


def test_select_language_respects_priority():
    lang = select_language(
        available=["python3", "cpp"],
        platform="leetcode",
        priority=["Java", "Python3"],
    )
    assert lang.name == "Python3"


def test_select_language_returns_none_if_unavailable():
    with pytest.raises(UnsupportedLanguageError):
        select_language(available=["C++"], platform="leetcode", priority=["Java"])
