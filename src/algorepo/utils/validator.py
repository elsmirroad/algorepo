from urllib.parse import urlparse

from algorepo.config import Config
from algorepo.exceptions import UnsupportedPlatformError
from algorepo.platforms import CodeWarsPlatform, LeetCodePlatform, Platform

DOMAINS = {
      "leetcode.com": "leetcode",
      "www.codewars.com": "codewars",
  }

PLATFORMS = {
    "leetcode": LeetCodePlatform,
    "codewars": CodeWarsPlatform,
}

NAMES = {
    "leetcode": "LeetCode",
    "codewars": "CodeWars",
}


def validate_url(url: str) -> str:
    domain = urlparse(url).hostname
    if domain in DOMAINS:
        return DOMAINS[domain]
    raise UnsupportedPlatformError()


def get_platform(name: str, config: Config) -> Platform:
    return PLATFORMS[name](config=config)
