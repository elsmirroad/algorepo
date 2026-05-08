from pydantic import BaseModel, HttpUrl


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
