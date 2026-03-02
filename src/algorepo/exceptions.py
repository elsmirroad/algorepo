class AlgorepoError(Exception):
    """Base project exception"""

class NetworkError(AlgorepoError):
    """Network Error (Timeout, DNS, HTTP 4xx/5xx)"""

class ProblemNotFoundError(AlgorepoError):
    """Problem was not found on Platform"""

class UnsupportedLanguageError(AlgorepoError):
    """Noone language from priority is supported"""

class ConfigError(AlgorepoError):
    """Configuration Error"""

class UnsupportedPlatformError(AlgorepoError):
    """Platform is not supported"""

class SolutionsListError(AlgorepoError):
    """Solutions was not found in Solutions directory"""
