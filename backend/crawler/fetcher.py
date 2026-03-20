from dataclasses import asdict, dataclass
from urllib.parse import urlparse

import httpx

from backend.config import settings

from backend.crawler.extractor import extract_clean_text
from backend.crawler.robots import is_allowed

try:
    from playwright.async_api import async_playwright
except Exception:  # pragma: no cover - optional dependency in local runtime
    async_playwright = None


@dataclass
class FetchedPage:
    url: str
    status: int
    raw_html: str = ""
    clean_text: str = ""
    final_url: str | None = None
    error: str | None = None
    blocked_by_robots: bool = False


async def _fetch_with_httpx(url: str, timeout_ms: int) -> FetchedPage:
    timeout_seconds = max(timeout_ms, 1) / 1000.0
    headers = {"User-Agent": "CRMindBot/1.0"}
    async with httpx.AsyncClient(follow_redirects=True, timeout=timeout_seconds) as client:
        try:
            response = await client.get(url, headers=headers)
            return FetchedPage(
                url=url,
                status=response.status_code,
                raw_html=response.text,
                final_url=str(response.url),
            )
        except Exception as exc:  # pragma: no cover - network/runtime dependent
            return FetchedPage(url=url, status=0, error=str(exc))


async def _fetch_with_playwright(url: str, timeout_ms: int) -> FetchedPage:
    if async_playwright is None:
        return FetchedPage(url=url, status=0, error="playwright_unavailable")

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(url, wait_until="networkidle", timeout=max(timeout_ms, 1000))
            html = await page.content()
            return FetchedPage(url=url, status=200, raw_html=html, final_url=page.url)
        except Exception as exc:  # pragma: no cover - network/runtime dependent
            return FetchedPage(url=url, status=0, error=str(exc))
        finally:
            await browser.close()


async def fetch_page(
    url: str,
    use_browser: bool = False,
    respect_robots: bool = True,
    timeout_ms: int = 15000,
) -> dict:
    if respect_robots and not is_allowed(url):
        return asdict(FetchedPage(url=url, status=403, blocked_by_robots=True, error="blocked_by_robots"))

    forced_domains = {
        domain.strip().lower()
        for domain in settings.crawl_use_browser_domains.split(",")
        if domain.strip()
    }
    domain = urlparse(url).netloc.lower()
    should_use_browser = use_browser or (domain in forced_domains)

    fetched = await (_fetch_with_playwright(url=url, timeout_ms=timeout_ms) if should_use_browser else _fetch_with_httpx(url=url, timeout_ms=timeout_ms))
    if fetched.raw_html:
        fetched.clean_text = extract_clean_text(fetched.raw_html)

    # Retry via browser for JS-heavy pages when static extraction is sparse.
    if not should_use_browser and fetched.status == 200 and len(fetched.clean_text) < 500:
        browser_fetched = await _fetch_with_playwright(url=url, timeout_ms=timeout_ms)
        if browser_fetched.status == 200 and browser_fetched.raw_html:
            browser_fetched.clean_text = extract_clean_text(browser_fetched.raw_html)
            if len(browser_fetched.clean_text) > len(fetched.clean_text):
                fetched = browser_fetched

    return asdict(fetched)
