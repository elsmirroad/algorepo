from enum import Enum


class ProblemErrorReason(str, Enum):
    NOT_FOUND = "not_found"
    UNAVAILABLE = "unavailable"


class LanguageErrorReason(str, Enum):
    NOT_SUPPORTED = "not_supported"
    NOT_AVAILABLE = "not_available"
    NO_MATCH = "no_match"


class ConfigErrorReason(str, Enum):
    INVALID_FORMAT = "invalid_format"
    EDITOR = "editor"
    PERMISSION = "permission"


class AlgorepoError(Exception):
    """Base project exception"""


class NetworkError(AlgorepoError):
    """Network Error (Timeout, DNS, HTTP 4xx/5xx)"""


class ProblemNotFoundError(AlgorepoError):
    """Problem was not found on Platform"""

    def __init__(
        self,
        reason: ProblemErrorReason,
        url: str,
        platform_name: str,
    ) -> None:
        self.reason = reason
        self.url = url
        self.platform_name = platform_name

        if self.reason == ProblemErrorReason.NOT_FOUND:
            message = f"Problem was not found on platform {self.platform_name} at URL: {self.url}"
        elif self.reason == ProblemErrorReason.UNAVAILABLE:
            message = (
                f"Problem is unavailable (Premium/Contest/Private) "
                f"on platform {self.platform_name} at URL: {self.url}"
            )
        else:
            message = f"Unknown problem error on {self.platform_name} at URL: {self.url}"

        super().__init__(message)


class UnsupportedLanguageError(AlgorepoError):
    """Noone language from priority is supported"""

    def __init__(
        self,
        reason: LanguageErrorReason,
        language: str,
        supported: list[str],
        available: list[str],
    ):
        self.reason = reason
        self.language = language
        self.supported = supported
        self.available = available

        if self.reason == LanguageErrorReason.NOT_SUPPORTED:
            message = (
                f"Language '{self.language}' is not supported by algorepo. "
                f"Supported languages: {', '.join(self.supported)}"
            )
        elif self.reason == LanguageErrorReason.NOT_AVAILABLE:
            message = (
                f"Language '{self.language}' is not available for this problem. "
                f"Available languages: {', '.join(self.available)}"
            )
        elif self.reason == LanguageErrorReason.NO_MATCH:
            message = (
                "None of the languages from your priority list are available for this problem. "
                f"Available languages: {', '.join(self.available)}"
            )
        else:
            message = "Unsupported language error"

        super().__init__(message)


class ConfigurationError(AlgorepoError):
    """Configuration Error"""

    def __init__(
        self,
        reason: ConfigErrorReason,
        path: str | None,
        editor: str | None,
    ) -> None:
        self.reason = reason
        self.path = path
        self.editor = editor

        if self.reason == ConfigErrorReason.INVALID_FORMAT:
            message = f"Invalid config format in: {self.path}"
        elif self.reason == ConfigErrorReason.EDITOR:
            message = (
                f"Failed to open editor '{self.editor}'. Make sure it's installed and in PATH."
            )
        elif self.reason == ConfigErrorReason.PERMISSION:
            if self.path:
                message = f"Permission denied: cannot read config file {self.path}"
            else:
                message = "Permission denied: cannot open editor"
        else:
            message = "Configuration error"

        super().__init__(message)


class UnsupportedPlatformError(AlgorepoError):
    """Platform is not supported"""


class SolutionsListError(AlgorepoError):
    """Solutions was not found in Solutions directory"""


class AuthorizationError(AlgorepoError):
    """Authorization Error"""
