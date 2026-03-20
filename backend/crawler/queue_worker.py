import asyncio

from backend.config import settings
from backend.crawler.chunker import chunk_with_metadata
from backend.crawler.extractor import extract_clean_text
from backend.crawler.rate_limiter import rate_limited_fetch
from backend.crawler.store import compute_content_hash, embed_and_store_chunks, store_source_document
from backend.services.signal_extractor import extract_signals


async def crawl_worker(db_pool, embed_service, batch_size: int = 10) -> None:
    while True:
        async with db_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, url, entity_id, entity_type, attempts, max_attempts
                FROM crawl_queue
                WHERE status = 'pending' AND scheduled_at <= NOW()
                ORDER BY priority ASC, scheduled_at ASC
                LIMIT $1
                FOR UPDATE SKIP LOCKED
                """,
                batch_size,
            )

            for row in rows:
                await process_crawl_item(dict(row), conn, embed_service)

        if not rows:
            await asyncio.sleep(10)


async def process_crawl_item(item: dict, db, embed_service) -> None:
    await db.execute(
        "UPDATE crawl_queue SET status='in_progress', started_at=NOW() WHERE id=$1::uuid",
        item["id"],
    )

    try:
        fetched = await rate_limited_fetch(
            item["url"],
            min_delay=settings.crawl_min_delay_seconds,
            timeout_ms=settings.crawl_timeout_ms,
            respect_robots=settings.respect_robots_txt,
        )
        if fetched.get("status") != 200:
            raise RuntimeError(f"crawl_http_status_{fetched.get('status')}")

        clean_text = fetched.get("clean_text") or extract_clean_text(fetched.get("raw_html", ""))
        content_hash = compute_content_hash(clean_text)

        existing = await db.fetchrow(
            "SELECT id, content_hash FROM source_documents WHERE source_url=$1 ORDER BY fetched_at DESC LIMIT 1",
            fetched["url"],
        )

        if existing and existing["content_hash"] == content_hash:
            await db.execute(
                "UPDATE source_documents SET last_seen_at=NOW() WHERE id=$1::uuid",
                existing["id"],
            )
        else:
            entity_info = {
                "entity_id": item.get("entity_id"),
                "entity_type": item.get("entity_type"),
            }
            doc_id = await store_source_document(db, fetched, clean_text, content_hash, entity_info)
            chunks = chunk_with_metadata(clean_text, fetched["url"], item.get("entity_id"))
            await embed_and_store_chunks(db, embed_service, doc_id, chunks, entity_info)

            # Extract and persist business signals from newly ingested content.
            if item.get("entity_id") and item.get("entity_type"):
                signals = await extract_signals(clean_text, str(item["entity_id"]), str(item["entity_type"]), fetched["url"])
                for signal in signals:
                    await db.execute(
                        """
                        INSERT INTO signals (
                            entity_id, entity_type, signal_type, description,
                            confidence, impact_score, source_url, event_date, source_doc_id
                        )
                        VALUES ($1::uuid, $2::entity_type, $3::signal_type, $4, $5, $6, $7, $8::date, $9::uuid)
                        """,
                        signal["entity_id"],
                        signal["entity_type"],
                        signal["signal_type"],
                        signal["description"],
                        signal["confidence"],
                        signal["impact_score"],
                        signal["source_url"],
                        signal.get("event_date"),
                        doc_id,
                    )

        await db.execute(
            "UPDATE crawl_queue SET status='completed', completed_at=NOW(), error_message=NULL WHERE id=$1::uuid",
            item["id"],
        )
    except Exception as exc:
        attempts = int(item.get("attempts", 0)) + 1
        max_attempts = int(item.get("max_attempts", settings.crawl_max_attempts))
        next_delay_seconds = 2**attempts

        if attempts >= max_attempts:
            await db.execute(
                """
                UPDATE crawl_queue
                SET status='failed', attempts=$2, error_message=$3, completed_at=NOW()
                WHERE id=$1::uuid
                """,
                item["id"],
                attempts,
                str(exc),
            )
            return

        await db.execute(
            """
            UPDATE crawl_queue
            SET status='pending', attempts=$2, error_message=$3,
                scheduled_at=NOW() + make_interval(secs => $4)
            WHERE id=$1::uuid
            """,
            item["id"],
            attempts,
            str(exc),
            next_delay_seconds,
        )


async def process_crawl_item_by_id(db, embed_service, crawl_item_id: str) -> None:
    row = await db.fetchrow(
        "SELECT id, url, entity_id, entity_type, attempts, max_attempts FROM crawl_queue WHERE id=$1::uuid",
        crawl_item_id,
    )
    if row is None:
        return
    await process_crawl_item(dict(row), db, embed_service)
