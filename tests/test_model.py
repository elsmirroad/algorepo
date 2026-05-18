import pytest
from pydantic import HttpUrl, ValidationError

from algorepo.models import Problem


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


def test_platform_creation(valid_problem_data):
    problem = Problem(**valid_problem_data)

    assert problem.problem_id == "1"
    assert problem.title == "Two Sum"
    assert problem.platform == "leetcode"
    assert problem.difficulty == "Easy"
    assert problem.description == "Some description"
    assert isinstance(problem.url, HttpUrl)
    assert problem.code_snippets["python3"] == "print('hi')"
    assert problem.sample_test_case == "Input: ... Output: ..."
    assert problem.is_premium is False
    assert problem.is_contest is False


@pytest.mark.parametrize(
    "missing_field",
    [
        "problem_id",
        "title",
        "platform",
        "difficulty",
        "description",
        "url",
    ],
)
def test_missing_required_fields(valid_problem_data, missing_field):
    data = valid_problem_data.copy()
    data.pop(missing_field)

    with pytest.raises(ValidationError):
        Problem(**data)


def test_sample_test_case_optional(valid_problem_data):
    data = valid_problem_data.copy()
    data["sample_test_case"] = None

    problem = Problem(**data)
    assert problem.sample_test_case is None


def test_url_auto_cast(valid_problem_data):
    problem = Problem(**valid_problem_data)
    assert isinstance(problem.url, HttpUrl)


def test_code_snippets_default_isolation():
    p1 = Problem(
        problem_id="1",
        title="A",
        platform="leetcode",
        difficulty="Easy",
        description="desc",
        url=HttpUrl("https://leetcode.com/problems/two-sum/"),
    )

    p2 = Problem(
        problem_id="2",
        title="B",
        platform="leetcode",
        difficulty="Easy",
        description="desc",
        url=HttpUrl("https://leetcode.com/problems/two-sum/"),
    )

    p1.code_snippets["python"] = "print(1)"

    assert "python" not in p2.code_snippets


def test_model_dump(valid_problem_data):
    problem = Problem(**valid_problem_data)
    dumped = problem.model_dump()

    assert dumped["problem_id"] == "1"
    assert dumped["platform"] == "leetcode"
    assert isinstance(dumped["url"], HttpUrl)


def test_model_dump_json(valid_problem_data):
    problem = Problem(**valid_problem_data)
    json_data = problem.model_dump_json()

    assert isinstance(json_data, str)
    assert "Two Sum" in json_data


def test_model_equality(valid_problem_data):
    p1 = Problem(**valid_problem_data)
    p2 = Problem(**valid_problem_data)

    assert p1 == p2


def test_model_inequality(valid_problem_data):
    p1 = Problem(**valid_problem_data)
    data = valid_problem_data.copy()
    data["problem_id"] = "2"
    p2 = Problem(**data)

    assert p1 != p2


def test_extra_fields_forbidden(valid_problem_data):
    data = valid_problem_data.copy()
    data["unexpected"] = "boom"

    problem = Problem(**data)

    assert not hasattr(problem, "unexpected")
