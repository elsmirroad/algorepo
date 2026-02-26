from pydantic import BaseModel, HttpUrl


class Problem(BaseModel):
    id: str
    title: str
    platform: str
    difficulty: str
    description: str
    url: HttpUrl
    code_snippets: dict[str, str] = {}
    sample_test_case: str | None = None
