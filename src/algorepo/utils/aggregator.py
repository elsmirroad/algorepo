from pathlib import Path


def sort_key(filename: str) -> tuple:
    try:
        prefix, _ = filename.split(". ")
        if prefix.isdigit():
            return (False, int(prefix))
        else:
            return (True, prefix)
    except Exception:
        return (True, filename)


def get_list(start_dir: Path) -> dict:
    """Get data of all solutions
    Output like LeetCode: ["1. Two Sum", "2. Add Two Numbers"..]"""
    solutions: dict = {}
    for dir in start_dir.iterdir():
        if dir.is_dir():
            solutions[dir.name] = sorted(
                [f.name for f in dir.glob("*") if f.is_file()], key=sort_key
            )
    return solutions


def get_platform_list(start_dir: Path) -> dict:
    """Git data of Platform's solutions"""
    return {
        start_dir.name: sorted([f.name for f in start_dir.glob("*") if f.is_file()], key=sort_key)
    }
