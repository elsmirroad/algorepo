from algorepo.exceptions import (
    AuthorizationError,
    LanguageErrorReason,
    NetworkError,
    ProblemErrorReason,
    ProblemNotFoundError,
    UnsupportedLanguageError,
    UnsupportedPlatformError,
)


def test_network_error_message():
    exc = NetworkError("Timeout")
    assert "Timeout" in str(exc)


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
    exc = AuthorizationError("LeetCode")
    assert "LeetCode" in str(exc)


def test_unsupported_platform_message():
    url = "https://unknown.com"
    exc = UnsupportedPlatformError(url)
    assert url in str(exc)
