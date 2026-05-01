from algorepo.languages import Language
from algorepo.models import Problem


def render_solution_file(problem: Problem, language: Language, code: str) -> str:
    """Generate file's content"""
    comment: str = language.comment_symbol
    full_title: str = f"{problem.problem_id}. {problem.title}"
    separator: str = "=" * len(max((full_title, str(problem.url)), key=len))
    lines: list[str] = [
        f"{comment} {separator}",
        f"{comment} {full_title}",  # Number + Problem Title
        f"{comment} {problem.url}",  # Problem url
        f"{comment} {separator}\n\n",
        f"{code}\n\n",
    ]
    tester: str = language.tester.get(problem.platform, "")
    if tester: # Custom testers for Language and Platform
        lines.insert(0, tester)
    if language.footer:
        lines.append(language.footer.format(description=problem.description))
    else:
        for line in problem.description.splitlines():
            lines.append(f"{comment} {line}")

    return "\n".join(lines)
