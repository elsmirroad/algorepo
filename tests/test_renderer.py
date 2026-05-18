import pytest

from algorepo.languages import Language
from algorepo.models import Problem
from algorepo.utils import render_solution_file


@pytest.fixture
def valid_problem_data():
    return {
        "problem_id": "1",
        "title": "Two Sum",
        "platform": "leetcode",
        "difficulty": "Easy",
        "description": "Some description",
        "url": "https://leetcode.com/problems/two-sum/",
        "code_snippets": {"python3": "print('hi')"},
        "sample_test_case": "Input: ... Output: ...",
    }


@pytest.fixture
def valid_language_data():
    return {
        "name": "Python3",
        "extension": ".py",
        "comment_symbol": "#",
        "tester": {"leetcode": "from lc import *"},
        "platform_ids": {"leetcode": "python3"},
        "footer": 'test("""\n{description}\n""")',
    }


def test_render(valid_problem_data, valid_language_data):
    problem = Problem(**valid_problem_data)
    language = Language(**valid_language_data)

    file = render_solution_file(
        problem=problem,
        language=language,
        code=problem.code_snippets[language.platform_ids["leetcode"]],
    )

    assert "from lc import *" in file
    assert "Two Sum" in file
    assert "print('hi')" in file
    assert "Some description" in file
