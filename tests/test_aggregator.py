from pathlib import Path

from algorepo.utils.aggregator import get_list, get_platform_list, sort_key


def test_sort_key():
    # Numbered prefix
    assert sort_key("1. Two Sum.py") == (False, 1)
    assert sort_key("100. Something.py") == (False, 100)

    # Non-numbered prefix (but has ". ")
    assert sort_key("String. Manipulation.py") == (True, "String")

    # No prefix format (raises Exception in split)
    assert sort_key("just_some_file.py") == (True, "just_some_file.py")


def test_get_list(tmp_path: Path):
    # Setup mock file structure
    leetcode_dir = tmp_path / "LeetCode"
    leetcode_dir.mkdir()
    (leetcode_dir / "1. Two Sum.py").touch()
    (leetcode_dir / "2. Add Two Numbers.py").touch()

    codewars_dir = tmp_path / "CodeWars"
    codewars_dir.mkdir()
    (codewars_dir / "Even or Odd | 1234.py").touch()

    # Create a random file that should not be a directory
    (tmp_path / "random.txt").touch()

    result = get_list(tmp_path)

    assert "LeetCode" in result
    assert "CodeWars" in result
    assert "random.txt" not in result

    assert result["LeetCode"] == ["1. Two Sum.py", "2. Add Two Numbers.py"]
    assert result["CodeWars"] == ["Even or Odd | 1234.py"]


def test_get_platform_list(tmp_path: Path):
    leetcode_dir = tmp_path / "LeetCode"
    leetcode_dir.mkdir()
    (leetcode_dir / "2. Add Two Numbers.py").touch()
    (leetcode_dir / "1. Two Sum.py").touch()

    result = get_platform_list(leetcode_dir)
    assert "LeetCode" in result

    # Check sorting
    assert result["LeetCode"] == ["1. Two Sum.py", "2. Add Two Numbers.py"]
