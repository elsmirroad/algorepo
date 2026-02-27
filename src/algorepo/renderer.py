from algorepo.languages import Language
from algorepo.models import Problem


def render_solution_file(problem: Problem, language: Language, code: str) -> str:
    """Generate file's content"""
    comment = language.comment_symbol
    full_title = f"{problem.id}. {problem.title}"
    separator = "=" * len(max((full_title, str(problem.url)), key=len))
    lines = [
        f"{comment} {separator}",
        f"{comment} {full_title}", # Number + Problem Title
        f"{comment} {problem.url}", # Problem url
        f"{comment} {separator}\n\n",
        f"{code}\n\n",
    ]
    if language.tester:
        lines.insert(0, language.tester)
    if language.footer: # Footer for tests
        lines.append(language.footer.format(description=problem.description))
    else:
        for line in problem.description.splitlines():
            lines.append(f"{comment} {line}")

    return "\n".join(lines)
