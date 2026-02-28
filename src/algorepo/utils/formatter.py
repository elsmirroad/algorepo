colors: dict[str, tuple] = {
    "g": ('[green]', '[/green]'),
    "y": ('[yellow]', '[/yellow]'),
    "r": ('[red]', '[/red]'),
    "w": ('[white]', '[/white]'),
}


def get_difficulty_color(difficulty):
    dc = {
        "Easy": colors['g'],
        "Medium": colors['y'],
        "Hard": colors['r'],
        "": colors['w'],
    }
    color = dc.get(difficulty, colors['w'])
    return f"{color[0]}[{difficulty}]{color[1]}"


def format_result(
        problem_id: str,
        problem: str,
        difficulty: str,
        language: str,
        filepath: str,
) -> str:
    difficulty = get_difficulty_color(difficulty)
    c = colors['w']
    return f"""
{c[0]}{problem_id}. {problem}{c[1]} {difficulty}
{c[0]}{language}{c[1]}
{c[0]}{filepath}{c[1]}
"""
