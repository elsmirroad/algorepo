class AlgorepoError(Exception):
    """Base project exception"""


class NetworkError(AlgorepoError):
    """Network Error (Timeout, DNS, HTTP 4xx/5xx)"""


class ProblemNotFoundError(AlgorepoError):
    """Problem was not found on Platform"""


class UnsupportedLanguageError(AlgorepoError):
    """Noone language from priority is supported"""

    def __init__(
        self,
        reason: str,
        *,
        language: str = "",
        supported: list[str] = [],
        available: list[str] = [],
    ):
        self.reason = reason
        self.language = language
        self.supported = supported
        self.available = available

    def __str__(self):
        if self.reason == "not_supported":
            return (
                f"Language '{self.language}' is not supported by algorepo."
                f"Supported languages: {', '.join(self.supported)}"
            )

        elif self.reason == "not_available":
            return (
                f"Language '{self.language}' is not available for this problem."
                f"Available languages: {', '.join(self.available)}"
            )

        elif self.reason == "no_match":
            return (
                "None of the languages from your priority list are available for this problem."
                f"Available languages: {', '.join(self.available)}"
            )
        return "Unsupported language error"


class ConfigurationError(AlgorepoError):
    """Configuration Error"""

    def __init__(
        self,
        reason: str,
        *,
        path: str | None = None,
        editor: str | None = None,
    ) -> None:
        self.reason = reason
        self.path = path
        self.editor = editor

    def __str__(self):
        if self.reason == "not_found":
            return f"Config file was not found: {self.path}"
        elif self.reason == "invalid_format":
            return f"Invalid config format in: {self.path}"
        elif self.reason == "editor":
            return f"Failed to open editor '{self.editor}'. Make sure it's installed and in PATH."
        elif self.reason == "permission":
            if self.path:
                return f"Permission denied: cannot read config file {self.path}"
            return "Permission denied: cannot open editor"
        return "Configuration error"


class UnsupportedPlatformError(AlgorepoError):
    """Platform is not supported"""


class SolutionsListError(AlgorepoError):
    """Solutions was not found in Solutions directory"""


class AuthorizationError(AlgorepoError):
    """Authorization Error"""
