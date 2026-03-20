import asyncio
import hashlib

from backend.database import close_pool, create_pool, get_pool


async def main() -> None:
    await create_pool()
    pool = await get_pool()

    companies = [
        ("comp_example_inc", "Example Inc", "example.com", "SaaS"),
        ("comp_nimbus_data", "Nimbus Data", "nimbusdata.ai", "Data Infrastructure"),
        ("comp_lumina_health", "Lumina Health", "luminahealth.com", "HealthTech"),
        ("comp_orbit_logistics", "Orbit Logistics", "orbitlogistics.io", "Logistics"),
        ("comp_polar_finance", "Polar Finance", "polarfinance.co", "FinTech"),
    ]

    async with pool.acquire() as db:
        company_ids = {}
        for canonical_id, name, domain, industry in companies:
            company_id = await db.fetchval(
                """
                INSERT INTO companies (canonical_id, canonical_name, domain, industry)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (canonical_id) DO UPDATE SET canonical_name=EXCLUDED.canonical_name
                RETURNING id
                """,
                canonical_id,
                name,
                domain,
                industry,
            )
            company_ids[canonical_id] = company_id

        people_count = 0
        for canonical_id, _, _, _ in companies:
            company_id = company_ids[canonical_id]
            for idx in range(4):
                full_name = f"{canonical_id.split('_')[1].title()} Person {idx + 1}"
                await db.execute(
                    """
                    INSERT INTO people (canonical_id, full_name, current_title, seniority_level, current_company_id)
                    VALUES ($1, $2, $3, $4::seniority_level, $5::uuid)
                    ON CONFLICT (canonical_id) DO NOTHING
                    """,
                    f"pers_{canonical_id}_{idx + 1}",
                    full_name,
                    ["Engineer", "Manager", "Director", "VP"][idx % 4],
                    ["mid", "senior", "director", "vp"][idx % 4],
                    company_id,
                )
                people_count += 1

        signals = [
            ("hiring", "Hiring for backend engineers"),
            ("funding", "Closed a growth round"),
            ("product_launch", "Launched AI assistant"),
            ("expansion", "Opened EU office"),
            ("leadership_change", "Hired new CTO"),
        ]
        signal_count = 0
        for idx, (canonical_id, _, domain, _) in enumerate(companies):
            company_id = company_ids[canonical_id]
            signal_type, desc = signals[idx % len(signals)]
            await db.execute(
                """
                INSERT INTO signals (entity_id, entity_type, signal_type, description, confidence, impact_score, source_url)
                VALUES ($1::uuid, 'company', $2::signal_type, $3, 0.8, 0.7, $4)
                """,
                company_id,
                signal_type,
                desc,
                f"https://{domain}/news",
            )
            signal_count += 1

        source_count = 0
        chunk_count = 0
        for canonical_id, name, domain, _ in companies:
            company_id = company_ids[canonical_id]
            clean_text = f"{name} is expanding rapidly and hiring experienced engineers in 2026."
            source_id = await db.fetchval(
                """
                INSERT INTO source_documents (source_url, source_type, clean_text, content_hash, entity_id, entity_type)
                VALUES ($1, 'company_website', $2, $3, $4::uuid, 'company')
                RETURNING id
                """,
                f"https://{domain}/about",
                clean_text,
                hashlib.sha256(clean_text.encode("utf-8")).hexdigest(),
                company_id,
            )
            source_count += 1

            embedding = [0.01] * 768
            await db.execute(
                """
                INSERT INTO chunks (
                    source_doc_id, chunk_index, chunk_text, entity_id, entity_type,
                    embedding, embed_model_id, freshness_score, trust_score
                )
                VALUES ($1::uuid, 0, $2, $3::uuid, 'company', $4::vector, 'nomic-embed-text', 0.8, 0.8)
                """,
                source_id,
                clean_text,
                company_id,
                embedding,
            )
            chunk_count += 1

    await close_pool()
    print(f"Inserted companies={len(companies)} people={people_count} signals={signal_count} source_documents={source_count} chunks={chunk_count}")


if __name__ == "__main__":
    asyncio.run(main())
