import asyncio
from collections import defaultdict
from urllib.parse import urlparse

from backend.crawler.fetcher import fetch_page

_last_request_time: dict[str, float] = defaultdict(float)
_domain_locks: dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)


async def rate_limited_fetch(url: str, min_delay: float = 3.0, **kwargs) -> dict:
    domain = urlparse(url).netloc
    lock = _domain_locks[domain]

    async with lock:
        now = asyncio.get_running_loop().time()
        elapsed = now - _last_request_time[domain]
        if elapsed < min_delay:
            await asyncio.sleep(min_delay - elapsed)

        result = await fetch_page(url, **kwargs)
        _last_request_time[domain] = asyncio.get_running_loop().time()
        return result
