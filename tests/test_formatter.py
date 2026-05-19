from algorepo.utils.formatter import format_list, format_result


def test_format_result():
    res = format_result(
        problem_id="1",
        problem="Two Sum",
        difficulty="Easy",
        language="Python3",
        filepath="~/Solutions/LeetCode/1. Two Sum.py",
    )

    assert "Two Sum" in res
    assert "[Easy]" in res
    assert "Python3" in res


def test_format_list():
    solutions = {
        "LeetCode": ["1. Two Sum.py", "2. Add Two Numbers.py"],
        "CodeWars": ["Even or Odd.py"],
    }
    res = format_list(solutions)

    assert "SOLUTIONS" in res
    assert "LeetCode" in res
    assert "1. Two Sum.py" in res
    assert "CodeWars" in res
