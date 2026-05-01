from dataclasses import dataclass

from algorepo.exceptions import UnsupportedLanguageError


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
        if preferred in LANGUAGES:
            lang = LANGUAGES[preferred]
            if lang.platform_ids.get(platform) in available:
                return lang
            else:
                raise UnsupportedLanguageError()
        else:
            raise UnsupportedLanguageError()

    for lang in priority:
        if lang in LANGUAGES:
            lang = LANGUAGES[lang]
            if lang.platform_ids.get(platform) in available:
                return lang
    raise UnsupportedLanguageError()


LANGUAGES: dict[str, Language] = {
    "Python3": Language(
        name="Python3",
        extension=".py",
        comment_symbol="#",
        tester={"leetcode": "from lc import *", "codewars": "from cw import *"},
        platform_ids={"leetcode": "python3", "codewars": "python"},
        footer='test("""\n{description}\n""")',
    ),
}
