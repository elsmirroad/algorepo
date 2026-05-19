from pathlib import Path

import pytest

from algorepo.config import Config
from algorepo.platforms import LeetCodePlatform
from algorepo.utils.tester import TestCase, extract_description, parse_signature


@pytest.fixture
def leetcode_platform():
    return LeetCodePlatform(Config())


def test_parse_description_basic(leetcode_platform):
    text = """
    Example 1:
    Input: nums = [2,7,11,15], target = 9
    Output: [0,1]
    Explanation: Because nums[0] + nums[1] == 9, we return [0, 1].
    """
    tests = leetcode_platform.extract_test_cases(text)
    assert len(tests) == 1
    assert tests[0].inputs == ["[2,7,11,15]", "9"]
    assert tests[0].expected == "[0,1]"


def test_parse_description_multiple(leetcode_platform):
    text = """
    Example 1:
    Input: s = "abcabcbb"
    Output: 3

    Example 2:
    Input: s = "bbbbb"
    Output: 1
    """
    tests = leetcode_platform.extract_test_cases(text)
    assert len(tests) == 2
    assert tests[0].inputs == ['"abcabcbb"']
    assert tests[0].expected == "3"
    assert tests[1].inputs == ['"bbbbb"']
    assert tests[1].expected == "1"


def test_parse_signature_cpp():
    text = "int lengthOfLongestSubstring(string s) {"
    sig = parse_signature(text, "C++")
    assert sig is not None
    assert sig.name == "lengthOfLongestSubstring"
    assert sig.return_type == "int"
    assert sig.args == [("s", "string")]


def test_parse_signature_rust():
    text = "pub fn two_sum(nums: Vec<int>, target: i32) -> Vec<i32>"
    sig = parse_signature(text, "Rust")
    assert sig is not None
    assert sig.name == "two_sum"
    assert sig.return_type == "Vec<i32>"
    assert len(sig.args) == 2
    assert sig.args[0] == ("nums", "Vec<int>")
    assert sig.args[1] == ("target", "i32")


def test_parse_signature_go():
    text = "func twoSum(nums []int, target int) []int"
    sig = parse_signature(text, "Go")
    assert sig is not None
    assert sig.name == "twoSum"
    assert sig.return_type == "[]int"
    assert len(sig.args) == 2
    assert sig.args[0] == ("nums", "[]int")
    assert sig.args[1] == ("target", "int")


def test_extract_description(tmp_path):
    file = tmp_path / "solution.py"
    file.write_text("# Input: x = 1\n# Output: 2\ndef func(): pass")
    desc = extract_description(file, "#")
    assert "Input: x = 1" in desc
    assert "Output: 2" in desc
