from urllib.parse import urlparse

from algorepo.exceptions import UnsupportedPlatformError
from algorepo.platforms.base import Platform
from algorepo.platforms.leetcode import LeetCodePlatform

DOMAINS = {
      "leetcode.com": "leetcode",
      "codewars.com": "codewars",
  }

PLATFORMS = {
    "leetcode": LeetCodePlatform(),
}


def validate_url(url: str) -> str:
    domain = urlparse(url).hostname
    if domain in DOMAINS:
        return DOMAINS[domain]
    raise UnsupportedPlatformError()


#WAITING: Get Config argument for Platform Class
def get_platform(name: str) -> Platform:
    return PLATFORMS[name]
