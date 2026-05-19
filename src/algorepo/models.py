from pydantic import BaseModel, HttpUrl


class TestCase(BaseModel):
    __test__ = False
    inputs: list[str]  # Raw strings of arguments, e.g. ["[2,7,11,15]", "9"]
    expected: str  # Raw string of expected result, e.g. "[0,1]"


class FunctionSignature(BaseModel):
    name: str
    args: list[tuple[str, str]]
    return_type: str


class Problem(BaseModel):
    problem_id: str
    title: str
    platform: str
    difficulty: str
    description: str
    url: HttpUrl
    preffered_lang: str | None = None
    code_snippets: dict[str, str] = {}
    available_languages: list[str] = []
    sample_test_case: str | None = None
    is_premium: bool = False
    is_contest: bool = False
