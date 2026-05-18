from algorepo.exceptions import (
    AuthorizationError,
    ConfigErrorReason,
    ConfigurationError,
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
    exc_http = NetworkError(
        platform_name="leetcode", reason=NetworkErrorReason.HTTP_ERROR, details="500 Server Error"
    )
    assert "HTTP Error" in str(exc_http)

    exc_conn = NetworkError("leetcode", NetworkErrorReason.CONNECTION_ERROR, "DNS failed")
    assert "Connection Error" in str(exc_conn)

    exc_timeout = NetworkError("leetcode", NetworkErrorReason.TIMEOUT, "Read timeout")
    assert "timed out" in str(exc_timeout)

    exc_decode = NetworkError("leetcode", NetworkErrorReason.DECODING_ERROR, "Invalid JSON")
    assert "Failed to parse response" in str(exc_decode)

    exc_unknown = NetworkError("leetcode", NetworkErrorReason.UNKNOWN, "Whoops")
    assert "Network error on" in str(exc_unknown)


def test_problem_not_found_message():
    url = "https://leetcode.com/problems/none"
    exc_nf = ProblemNotFoundError(
        reason=ProblemErrorReason.NOT_FOUND, url=url, platform_name="leetcode"
    )
    assert "Problem was not found" in str(exc_nf)

    exc_unav = ProblemNotFoundError(
        reason=ProblemErrorReason.UNAVAILABLE, url=url, platform_name="leetcode"
    )
    assert "Problem is unavailable" in str(exc_unav)


def test_unsupported_language_message():
    exc_no_match = UnsupportedLanguageError(
        reason=LanguageErrorReason.NO_MATCH,
        language="",
        supported=["python", "java"],
        available=["python", "cpp"],
    )
    assert "None of the languages from your priority list" in str(exc_no_match)

    exc_not_supported = UnsupportedLanguageError(
        reason=LanguageErrorReason.NOT_SUPPORTED,
        language="cobol",
        supported=["python", "java"],
        available=[],
    )
    assert "is not supported by algorepo" in str(exc_not_supported)

    exc_not_available = UnsupportedLanguageError(
        reason=LanguageErrorReason.NOT_AVAILABLE,
        language="java",
        supported=["python", "java"],
        available=["python"],
    )
    assert "is not available for this problem" in str(exc_not_available)


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


def test_configuration_error_message():
    exc_fmt = ConfigurationError(
        reason=ConfigErrorReason.INVALID_FORMAT, path="/config.yaml", editor=None
    )
    assert "Invalid config format" in str(exc_fmt)

    exc_editor = ConfigurationError(
        reason=ConfigErrorReason.EDITOR, path=None, editor="nvim"
    )
    assert "Failed to open editor 'nvim'" in str(exc_editor)

    exc_perm1 = ConfigurationError(
        reason=ConfigErrorReason.PERMISSION, path="/config.yaml", editor=None
    )
    assert "cannot read config file" in str(exc_perm1)

    exc_perm2 = ConfigurationError(
        reason=ConfigErrorReason.PERMISSION, path=None, editor=None
    )
    assert "cannot open editor" in str(exc_perm2)
