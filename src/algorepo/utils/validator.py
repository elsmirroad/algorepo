from urllib.parse import urlparse

from algorepo.config import Config
from algorepo.exceptions import UnsupportedPlatformError
from algorepo.platforms.base import Platform
from algorepo.platforms.leetcode import LeetCodePlatform

DOMAINS = {
      "leetcode.com": "leetcode",
      "codewars.com": "codewars",
  }

PLATFORMS = {
    "leetcode": LeetCodePlatform,
}

NAMES = {
    "leetcode": "LeetCode",
}


def validate_url(url: str) -> str:
    domain = urlparse(url).hostname
    if domain in DOMAINS:
        return DOMAINS[domain]
    raise UnsupportedPlatformError()


def get_platform(name: str, config: Config) -> Platform:
    return PLATFORMS[name](config=config)
