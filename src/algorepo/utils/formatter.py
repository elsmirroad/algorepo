colors: dict[str, tuple] = {
    "g": ("[green]", "[/green]"),
    "y": ("[yellow]", "[/yellow]"),
    "r": ("[red]", "[/red]"),
    "w": ("[white]", "[/white]"),
}


def get_difficulty_color(difficulty) -> str:
    """Get right color for fifficulty"""
    dc: dict[str, tuple] = {
        "Easy": colors["g"],
        "Medium": colors["y"],
        "Hard": colors["r"],
        "": colors["w"],
    }
    color = dc.get(difficulty, colors["w"])
    return f"{color[0]}[{difficulty}]{color[1]}"


def format_result(
    problem_id: str,
    problem: str,
    difficulty: str,
    language: str,
    filepath: str,
) -> str:
    """Get formated output for Solution creating"""
    difficulty = get_difficulty_color(difficulty)
    c = colors["w"]
    return f"""
{c[0]}{problem_id}. {problem}{c[1]} {difficulty}
{c[0]}{language}{c[1]}
{c[0]}{filepath}{c[1]}
"""


def format_list(solutions_list: dict) -> str:
    """Get formated output for list of solutions"""
    result: str = "SOLUTIONS:\n\n"
    for platform, solutions in solutions_list.items():
        result += platform + "\n"
        for solution in solutions:
            result += f"    {solution}\n"
        result += "\n"
    return result

