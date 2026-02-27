import pytest

from algorepo.exceptions import UnsupportedPlatformError
from algorepo.utils.validator import validate_url


def test_leetcode_url():
    result = validate_url("https://leetcode.com/problems/two-sum/")
    assert result == "leetcode"


def test_invalid_url():
    with pytest.raises(UnsupportedPlatformError):
        validate_url("https://google.com")
