from algorepo.exceptions import (
    AuthorizationError,
    LanguageErrorReason,
    NetworkError,
    NetworkErrorReason,
    ProblemErrorReason,
    ProblemNotFoundError,
    SolutionsListError,
    UnsupportedLanguageError,
    UnsupportedPlatformError,
)


def test_network_error_message():
    exc = NetworkError(
        platform_name="leetcode", reason=NetworkErrorReason.HTTP_ERROR, details="500 Server Error"
    )
    assert "leetcode" in str(exc)
    assert "500 Server Error" in str(exc)
    assert "HTTP Error" in str(exc)


def test_problem_not_found_message():
    url = "https://leetcode.com/problems/none"
    exc = ProblemNotFoundError(
        reason=ProblemErrorReason.NOT_FOUND, url=url, platform_name="leetcode"
    )
    assert url in str(exc)
    assert "Problem was not found" in str(exc)
    assert "leetcode" in str(exc)


def test_unsupported_language_no_match_message():
    exc = UnsupportedLanguageError(
        reason=LanguageErrorReason.NO_MATCH,
        language="",
        supported=["python", "java"],
        available=["python", "cpp"],
    )
    assert "None of the languages from your priority list" in str(exc)
    assert "python, cpp" in str(exc)


def test_authorization_error_message():
    exc = AuthorizationError(platform_name="leetcode")
    assert "leetcode" in str(exc)
    assert "Authorization failed for" in str(exc)


def test_unsupported_platform_message():
    exc = UnsupportedPlatformError(platform_name="unknown.com", supported=["leetcode", "codewars"])
    assert "unknown.com" in str(exc)
    assert "leetcode, codewars" in str(exc)


def test_solutions_list_error_message():
    exc = SolutionsListError(path="/non/existent/path")
    assert "/non/existent/path" in str(exc)
    assert "Solutions directory not found" in str(exc)
