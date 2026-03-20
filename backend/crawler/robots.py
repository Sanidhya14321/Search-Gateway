from functools import lru_cache
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser


@lru_cache(maxsize=512)
def get_robots_parser(domain: str) -> RobotFileParser:
    parser = RobotFileParser()
    parser.set_url(f"https://{domain}/robots.txt")
    try:
        parser.read()
    except Exception:
        return parser
    return parser


def is_allowed(url: str, user_agent: str = "CRMindBot") -> bool:
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return False

    parser = get_robots_parser(parsed.netloc)
    try:
        return parser.can_fetch(user_agent, url)
    except Exception:
        return True
