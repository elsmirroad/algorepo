import json
import re
from pathlib import Path

from algorepo.models import FunctionSignature, TestCase


def extract_description(filepath: Path, comment_symbol: str) -> str:
    """
    Extracts all commented lines from the file to search for test cases.
    Looks through the entire file.
    """
    description_lines = []
    # We look for common comment markers and JSDoc/C-style markers
    pattern = re.compile(r"^(\/\/|\/\*|\*\/|\*|#|--)\s*(.*)")

    with open(filepath, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            match = pattern.match(line)
            if match:
                description_lines.append(match.group(2))
            elif not line:
                # Keep empty lines to help parse_description separate blocks
                description_lines.append("")

    return "\n".join(description_lines)


def parse_signature(text: str, language: str) -> FunctionSignature | None:
    """
    Extracts function signature from description or code.
    Supported languages: C, C++, Rust, Go, Java, Kotlin.
    """
    patterns = {
        "C": r"([a-zA-Z0-9_* ]+)\s+([a-zA-Z0-9_]+)\s*\(([^)]*)\)",
        "C++": r"([a-zA-Z0-9_<>]+\*?)\s+([a-zA-Z0-9_]+)\s*\(([^)]*)\)",
        "Rust": r"fn\s+([a-zA-Z0-9_]+)\s*\(([^)]*)\)\s*->\s*([a-zA-Z0-9_<>\s]+)",
        "Go": r"func\s+([a-zA-Z0-9_]+)\s*\(([^)]*)\)\s*([a-zA-Z0-9_*\[\]]+)",
        "Java": r"(?:public\s+)?([a-zA-Z0-9_<>\s\[\]]+)\s+([a-zA-Z0-9_]+)\s*\(([^)]*)\)",
        "Kotlin": r"fun\s+([a-zA-Z0-9_]+)\s*\(([^)]*)\)\s*:\s*([a-zA-Z0-9_\[\]<>]+)",
    }

    pattern = patterns.get(language)
    if not pattern:
        return None

    match = re.search(pattern, text)
    if not match:
        return None

    if language in ("Rust", "Go", "Kotlin"):
        name = match.group(1).strip()
        raw_args = match.group(2).strip()
        ret_type = match.group(3).strip()
    else:  # C, C++, Java
        ret_type = match.group(1).strip()
        name = match.group(2).strip()
        raw_args = match.group(3).strip()

    # Parse arguments
    args = []
    if raw_args:
        # Simple split by comma, might need enhancement for complex types like pair<int, int>
        for part in raw_args.split(","):
            part = part.strip()
            if not part:
                continue
            if language in ("Rust", "Go", "Kotlin"):
                arg_parts = re.split(r"[:\s]+", part)
                if len(arg_parts) >= 2:
                    args.append((arg_parts[0], arg_parts[1]))
            else:
                arg_parts = part.rsplit(maxsplit=1)
                if len(arg_parts) >= 2:
                    args.append((arg_parts[1], arg_parts[0]))

    return FunctionSignature(name=name, args=args, return_type=ret_type)


def save_test_cases_to_json(test_cases: list[TestCase], path: Path) -> None:
    """Saves test cases to a JSON file for safe reading by runners."""
    data = [{"inputs": tc.inputs, "expected": tc.expected} for tc in test_cases]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)


def _to_cpp_recursive(data) -> str:
    """Internal helper for C++ literal conversion."""
    if isinstance(data, list):
        return "{" + ", ".join(_to_cpp_recursive(item) for item in data) + "}"
    if isinstance(data, bool):
        return "true" if data else "false"
    if isinstance(data, str):
        # json.dumps handles double quotes and escaping correctly for C++
        return json.dumps(data)
    if data is None:
        return "nullptr"
    return str(data)


def to_cpp_literal(val: str) -> str:
    """
    Safely converts a JSON-like string (from LeetCode/Codewars) to a C++ literal.
    Handles nested vectors, strings with special characters, and booleans.
    """
    try:
        data = json.loads(val)
        return _to_cpp_recursive(data)
    except json.JSONDecodeError:
        # If it's not valid JSON, we fallback to basic escaping
        return val.replace("'", '"')


def to_c_literal(val: str, type_hint: str = "") -> str:
    """
    Converts a JSON-like string to a C literal.
    Primarily handles strings and basic types for now.
    """
    try:
        data = json.loads(val)
        if isinstance(data, str):
            return json.dumps(data)
        if isinstance(data, bool):
            return "true" if data else "false"
        if data is None:
            return "NULL"
        return str(data)
    except json.JSONDecodeError:
        if "char" in type_hint:
            # Ensure it's quoted if it's supposed to be a string
            safe_val = val.replace('"', '\\"')
            return f'"{safe_val}"' if not val.startswith('"') else val
        return val
