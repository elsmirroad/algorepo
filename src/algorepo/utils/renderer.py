import string

from algorepo.languages import Language
from algorepo.models import Problem


def render_solution_file(
    problem: Problem, language: Language, code: str, template: string.Template
) -> str:
    """Generate file's content using a template"""
    comment: str = language.comment_symbol
    full_title: str = f"{problem.problem_id}. {problem.title}"

    max_len = max(len(full_title), len(str(problem.url)))
    separator_line = "=" * max_len

    header = (
        f"{comment} {separator_line}\n"
        f"{comment} {full_title}\n"
        f"{comment} {problem.url}\n"
        f"{comment} {separator_line}"
    )

    description = ""
    if not language.footer:
        desc_lines = []
        for line in problem.description.splitlines():
            desc_lines.append(f"{comment} {line}")
        description = "\n".join(desc_lines)

    tester_raw = language.tester.get(problem.platform, "")
    variables = {
        "header": header,
        "url": str(problem.url),
        "description": description,
        "code": code,
        "platform": problem.platform,
        "difficulty": problem.difficulty,
        "id": problem.problem_id,
        "tester": f"{tester_raw}\n" if tester_raw else "",
        "footer": language.footer.format(description=problem.description)
        if language.footer
        else "",
    }

    return template.safe_substitute(variables).strip() + "\n"
