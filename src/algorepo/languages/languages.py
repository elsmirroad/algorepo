from dataclasses import dataclass

from algorepo.exceptions import LanguageErrorReason, UnsupportedLanguageError


@dataclass
class Language:
    name: str
    extension: str
    comment_symbol: str
    platform_ids: dict[str, str]  # {"leetcode": "Python3"..}
    tester: dict[str, str]  # {"leetcode": "from lc import *", "codewars": "from cw import *"}
    footer: str | None = None


def select_language(
    available: list[str],
    platform: str,
    priority: list[str],
    preferred: str | None = None,
) -> Language:
    """Return first language from priority for Platform"""

    if preferred:
        if preferred not in LANGUAGES:
            raise UnsupportedLanguageError(
                reason=LanguageErrorReason.NOT_SUPPORTED,
                language=preferred,
                supported=list(LANGUAGES.keys()),
                available=available,
            )
        lang = LANGUAGES[preferred]
        if lang.platform_ids.get(platform) not in available:
            raise UnsupportedLanguageError(
                reason=LanguageErrorReason.NOT_AVAILABLE,
                language=preferred,
                supported=list(LANGUAGES.keys()),
                available=available,
            )
        return lang

    for lang in priority:
        if lang in LANGUAGES:
            lang = LANGUAGES[lang]
            if lang.platform_ids.get(platform) in available:
                return lang
    raise UnsupportedLanguageError(
        reason=LanguageErrorReason.NO_MATCH,
        language="",
        supported=list(LANGUAGES.keys()),
        available=available,
    )


LANGUAGES: dict[str, Language] = {
    "Python3": Language(
        name="Python3",
        extension=".py",
        comment_symbol="#",
        tester={"leetcode": "from lc import *", "codewars": "from cw import *"},
        platform_ids={"leetcode": "python3", "codewars": "python"},
        footer='test("""\n{description}\n""")',
    ),
    "Python": Language(
        name="Python",
        extension=".py",
        comment_symbol="#",
        tester={"leetcode": "from lc import *", "codewars": "from cw import *"},
        platform_ids={"leetcode": "python", "codewars": "python"},
        footer='test("""\n{description}\n""")',
    ),
    "C": Language(
        name="C",
        extension=".c",
        comment_symbol="//",
        tester={},
        platform_ids={"leetcode": "c", "codewars": "c"},
    ),
    "C++": Language(
        name="C++",
        extension=".cpp",
        comment_symbol="//",
        tester={},
        platform_ids={"leetcode": "cpp", "codewars": "cpp"},
    ),
    "Java": Language(
        name="Java",
        extension=".java",
        comment_symbol="//",
        tester={},
        platform_ids={"leetcode": "java", "codewars": "java"},
    ),
    "JavaScript": Language(
        name="JavaScript",
        extension=".js",
        comment_symbol="//",
        tester={},
        platform_ids={"leetcode": "javascript", "codewars": "javascript"},
    ),
    "TypeScript": Language(
        name="TypeScript",
        extension=".ts",
        comment_symbol="//",
        tester={},
        platform_ids={"leetcode": "typescript", "codewars": "typescript"},
    ),
    "Kotlin": Language(
        name="Kotlin",
        extension=".kt",
        comment_symbol="//",
        tester={},
        platform_ids={"leetcode": "kotlin", "codewars": "kotlin"},
    ),
    "Go": Language(
        name="Go",
        extension=".go",
        comment_symbol="//",
        tester={},
        platform_ids={"leetcode": "golang", "codewars": "go"},
    ),
    "Rust": Language(
        name="Rust",
        extension=".rs",
        comment_symbol="//",
        tester={},
        platform_ids={"leetcode": "rust", "codewars": "rust"},
    ),
    "C#": Language(
        name="C#",
        extension=".cs",
        comment_symbol="//",
        tester={},
        platform_ids={"leetcode": "csharp", "codewars": "csharp"},
    ),
    "Swift": Language(
        name="Swift",
        extension=".swift",
        comment_symbol="//",
        tester={},
        platform_ids={"leetcode": "swift", "codewars": "swift"},
    ),
    "PHP": Language(
        name="PHP",
        extension=".php",
        comment_symbol="//",
        tester={},
        platform_ids={"leetcode": "php", "codewars": "php"},
    ),
    "Ruby": Language(
        name="Ruby",
        extension=".rb",
        comment_symbol="#",
        tester={},
        platform_ids={"leetcode": "ruby", "codewars": "ruby"},
    ),
    "Scala": Language(
        name="Scala",
        extension=".scala",
        comment_symbol="//",
        tester={},
        platform_ids={"leetcode": "scala", "codewars": "scala"},
    ),
}
