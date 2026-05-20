import os
import shutil
from importlib.resources import files
from pathlib import Path

from algorepo.utils.validator import NAMES


def get_binary_path(name: str) -> Path | None:
    """Returns the full path to a binary if found in PATH or common locations."""
    # Standard check
    found = shutil.which(name)
    if found:
        return Path(found)

    # Check common locations
    extra_paths = [
        Path.home() / ".cargo" / "bin",  # Rust
        Path("/usr/local/bin"),
        Path("/opt/homebrew/bin"),  # macOS Homebrew
    ]

    for path in extra_paths:
        binary_path = path / name
        if binary_path.exists() and os.access(binary_path, os.X_OK):
            return binary_path

    return None


def check_binary(name: str) -> bool:
    """Checks if a binary/command is available."""
    return get_binary_path(name) is not None


def ensure_gitignore(solutions_dir: Path) -> bool:
    """
    Ensures that .gitignore exists and contains necessary rules for Algorepo.
    Returns True if updated/created.
    """

    gitignore_path = solutions_dir / ".gitignore"
    needed_rules = {
        "testers/",
        "*.out",
        "*.exe",
        "*.o",
        "*.obj",
        "bin/",
        "obj/",
        "__pycache__/",
        ".pytest_cache/",
        ".venv/",
    }

    if not gitignore_path.exists():
        content = (
            "# Algorepo: Ignored files and directories\n" + "\n".join(sorted(needed_rules)) + "\n"
        )
        gitignore_path.write_text(content, encoding="utf-8")
        return True

    content = gitignore_path.read_text(encoding="utf-8")
    lines = [line.strip() for line in content.splitlines()]
    current_rules = set(lines)

    missing_rules = needed_rules - current_rules
    if missing_rules:
        with open(gitignore_path, "a", encoding="utf-8") as f:
            f.write("\n# Added by Algorepo\n")
            for rule in sorted(missing_rules):
                f.write(f"{rule}\n")
        return True

    return False


def sync_testers(solutions_dir: Path) -> int:
    """
    Synchronizes tester templates from the package to the user's workspace.
    Returns the number of files updated/created.
    """

    testers_dest = solutions_dir / "testers"
    testers_src = files("algorepo.testers.templates")

    count = 0

    def copy_recursive(src, dest):
        nonlocal count
        dest.mkdir(parents=True, exist_ok=True)
        for item in src.iterdir():
            if item.is_dir():
                if item.name.startswith("__"):
                    continue
                copy_recursive(item, dest / item.name)
            else:
                dest_file = dest / item.name
                if (
                    not dest_file.exists()
                    or dest_file.stat().st_size != item.joinpath().stat().st_size
                ):
                    content = item.read_bytes()
                    dest_file.write_bytes(content)
                    count += 1

    copy_recursive(testers_src, testers_dest)
    return count


def get_problem_path(solutions_dir: Path, platform: str, filename: str) -> Path | None:
    """Finds a problem file by platform and filename."""

    platform_name = NAMES.get(platform, platform)
    target_dir = solutions_dir / platform_name
    if not target_dir.exists():
        return None

    exact_path = target_dir / filename
    if exact_path.exists():
        return exact_path

    # Improved matching: check for "{id}. " or "{id}." prefix to avoid ambiguous matches
    # e.g., prevents ID "1" from matching "10. Problem name"
    for item in target_dir.iterdir():
        if not item.is_file():
            continue

        name = item.name
        # Match "1. Two Sum" or "Two Sum"
        if name == filename or name.startswith(filename + ". ") or name.startswith(filename + "."):
            return item

        # Also try to match by exact ID before the first dot
        if "." in name:
            id_part = name.split(".")[0]
            if id_part == filename:
                return item

    return None
