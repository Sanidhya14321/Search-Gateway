---
name: web-crawler
description: >
  Implement the async web crawling layer for CRMind using Playwright. Use this skill
  when writing page fetching, dynamic rendering, HTML extraction, robots.txt checking,
  crawl queue management, or any ingestion code that retrieves raw web content.
  Keywords: crawler, Playwright, web scraping, fetch page, extract text, crawl queue,
  robots.txt, async crawl, HTML to text, ingestion.
---

## Design Principles

- **Respect robots.txt** by default. Set `respect_robots=False` only for private/authorized use.
- **Rate limit:** max 1 request per 3 seconds per domain (configurable).
- **Retry with backoff:** 3 attempts, exponential backoff (2s, 4s, 8s).
- **Playwright only for dynamic pages.** Use `httpx` for static pages (faster + cheaper).
- **Content hash:** store SHA-256 of clean_text; skip re-processing if unchanged.

---

## Page Fetcher

```python
import asyncio
import hashlib
from playwright.async_api import async_playwright
import httpx
from urllib.robotparser import RobotFileParser

async def fetch_page(
    url: str,
    use_browser: bool = False,
    respect_robots: bool = True,
    timeout_ms: int = 15000,
) -> FetchedPage:
    """
    Fetch a page. Use use_browser=True only for JS-heavy pages.
    Returns FetchedPage with raw_html, clean_text, http_status.
    """
    if respect_robots and not is_allowed(url):
        return FetchedPage(url=url, status=403, blocked_by_robots=True)

    if use_browser:
        return await _fetch_with_playwright(url, timeout_ms)
    else:
        return await _fetch_with_httpx(url, timeout_ms)


async def _fetch_with_httpx(url: str, timeout_ms: int) -> FetchedPage:
    async with httpx.AsyncClient(follow_redirects=True, timeout=timeout_ms / 1000) as client:
        headers = {"User-Agent": "CRMindBot/1.0 (+https://yourdomain.com/bot)"}
        try:
            resp = await client.get(url, headers=headers)
            return FetchedPage(
                url=url,
                status=resp.status_code,
                raw_html=resp.text,
                final_url=str(resp.url),
            )
        except Exception as e:
            return FetchedPage(url=url, status=0, error=str(e))


async def _fetch_with_playwright(url: str, timeout_ms: int) -> FetchedPage:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(url, wait_until="networkidle", timeout=timeout_ms)
            html = await page.content()
            return FetchedPage(url=url, status=200, raw_html=html, final_url=page.url)
        except Exception as e:
            return FetchedPage(url=url, status=0, error=str(e))
        finally:
            await browser.close()
```

---

## HTML → Clean Text Extraction

```python
from bs4 import BeautifulSoup
import re

def extract_clean_text(raw_html: str) -> str:
    """
    Strip boilerplate, keep meaningful text.
    """
    soup = BeautifulSoup(raw_html, "lxml")

    # Remove noise elements
    for tag in soup(["script", "style", "nav", "footer", "header",
                     "aside", "form", "noscript", "svg", "iframe"]):
        tag.decompose()

    # Get text, collapse whitespace
    text = soup.get_text(separator="\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()
```

---

## Robots.txt Checker

```python
from functools import lru_cache
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
import httpx

@lru_cache(maxsize=512)
def get_robots_parser(domain: str) -> RobotFileParser:
    rp = RobotFileParser()
    rp.set_url(f"https://{domain}/robots.txt")
    try:
        rp.read()
    except Exception:
        pass   # if no robots.txt, assume allowed
    return rp

def is_allowed(url: str, user_agent: str = "CRMindBot") -> bool:
    parsed = urlparse(url)
    domain = parsed.netloc
    rp = get_robots_parser(domain)
    return rp.can_fetch(user_agent, url)
```

---

## Domain Rate Limiter

```python
import asyncio
from collections import defaultdict

_last_request_time: dict[str, float] = defaultdict(float)
_domain_locks: dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)

async def rate_limited_fetch(url: str, min_delay: float = 3.0, **kwargs) -> FetchedPage:
    domain = urlparse(url).netloc
    async with _domain_locks[domain]:
        now = asyncio.get_event_loop().time()
        elapsed = now - _last_request_time[domain]
        if elapsed < min_delay:
            await asyncio.sleep(min_delay - elapsed)
        result = await fetch_page(url, **kwargs)
        _last_request_time[domain] = asyncio.get_event_loop().time()
        return result
```

---

## Crawl Queue Worker

```python
async def crawl_worker(db, embed_service, batch_size: int = 10):
    """
    Background worker: pulls from crawl_queue, fetches, extracts, chunks, embeds, stores.
    Designed to run as an ARQ or asyncio background task.
    """
    while True:
        # Pull pending items
        items = await db.fetch("""
            SELECT * FROM crawl_queue
            WHERE status = 'pending' AND scheduled_at <= NOW()
            ORDER BY priority ASC, scheduled_at ASC
            LIMIT $1
            FOR UPDATE SKIP LOCKED
        """, batch_size)

        for item in items:
            await process_crawl_item(item, db, embed_service)

        if not items:
            await asyncio.sleep(10)   # idle wait


async def process_crawl_item(item, db, embed_service):
    # Mark in progress
    await db.execute(
        "UPDATE crawl_queue SET status='in_progress', started_at=NOW() WHERE id=$1",
        item["id"]
    )
    try:
        fetched = await rate_limited_fetch(item["url"])
        if fetched.status != 200:
            raise ValueError(f"HTTP {fetched.status}")

        clean_text = extract_clean_text(fetched.raw_html)
        content_hash = hashlib.sha256(clean_text.encode()).hexdigest()

        # Check if content changed
        existing = await db.fetchrow(
            "SELECT content_hash FROM source_documents WHERE source_url=$1",
            item["url"]
        )
        if existing and existing["content_hash"] == content_hash:
            # Unchanged — just update last_seen_at
            await db.execute(
                "UPDATE source_documents SET last_seen_at=NOW() WHERE source_url=$1",
                item["url"]
            )
        else:
            # Store + chunk + embed
            doc_id = await store_source_document(db, fetched, clean_text, content_hash, item)
            chunks = chunk_text(clean_text)
            await embed_and_store_chunks(db, embed_service, doc_id, chunks, item)

        await db.execute(
            "UPDATE crawl_queue SET status='completed', completed_at=NOW() WHERE id=$1",
            item["id"]
        )
    except Exception as e:
        attempts = item["attempts"] + 1
        status = "failed" if attempts >= item["max_attempts"] else "pending"
        next_scheduled = f"NOW() + INTERVAL '{2 ** attempts} seconds'"
        await db.execute(f"""
            UPDATE crawl_queue
            SET status=$1, attempts=$2, error_message=$3,
                scheduled_at={next_scheduled}
            WHERE id=$4
        """, status, attempts, str(e), item["id"])
```

---

## Chunker

```python
def chunk_text(
    text: str,
    chunk_size: int = 512,
    chunk_overlap: int = 64,
) -> List[str]:
    """
    Recursive character-based chunking.
    Use langchain's RecursiveCharacterTextSplitter or implement manually.
    """
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_text(text)
```

---

## File locations

```
backend/
  crawler/
    fetcher.py           ← fetch_page, httpx + playwright
    extractor.py         ← extract_clean_text
    robots.py            ← is_allowed
    rate_limiter.py      ← rate_limited_fetch
    queue_worker.py      ← crawl_worker, process_crawl_item
    chunker.py           ← chunk_text
  tests/
    test_crawler.py
```

---

## Environment Variables Required

```bash
PLAYWRIGHT_BROWSER=chromium
CRAWL_MIN_DELAY_SECONDS=3
CRAWL_MAX_ATTEMPTS=3
CRAWL_TIMEOUT_MS=15000
RESPECT_ROBOTS_TXT=true
```