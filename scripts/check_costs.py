import argparse
import asyncio
from dataclasses import dataclass
from pathlib import Path
import sys

import asyncpg

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import settings


@dataclass
class CostReport:
    llm_calls_30d: int
    chunks_embedded_30d: int
    est_llm_usd: float
    est_embed_usd: float

    @property
    def total_usd(self) -> float:
        return self.est_llm_usd + self.est_embed_usd


async def build_cost_report(dsn: str) -> CostReport:
    conn = await asyncpg.connect(dsn)
    try:
        llm_calls_30d = await conn.fetchval(
            """
            SELECT COALESCE(SUM(llm_calls_count), 0)
            FROM agent_runs
            WHERE created_at >= NOW() - INTERVAL '30 days'
            """
        )
        chunks_embedded_30d = await conn.fetchval(
            """
            SELECT COUNT(*)
            FROM chunks
            WHERE created_at >= NOW() - INTERVAL '30 days'
            """
        )
    finally:
        await conn.close()

    llm_calls = int(llm_calls_30d or 0)
    embedded_chunks = int(chunks_embedded_30d or 0)

    # Lightweight budget estimate for alerting purposes.
    est_llm_usd = llm_calls * 0.002
    est_embed_usd = embedded_chunks * 0.00002

    return CostReport(
        llm_calls_30d=llm_calls,
        chunks_embedded_30d=embedded_chunks,
        est_llm_usd=est_llm_usd,
        est_embed_usd=est_embed_usd,
    )


async def _async_main(max_monthly_usd: float, dsn: str) -> int:
    try:
        report = await build_cost_report(dsn)
    except Exception as exc:
        print(f"ERROR: Unable to build cost report: {type(exc).__name__}: {exc}")
        return 2

    print(f"LLM calls (30d): {report.llm_calls_30d}")
    print(f"Embedded chunks (30d): {report.chunks_embedded_30d}")
    print(f"Estimated LLM cost: ${report.est_llm_usd:.2f}")
    print(f"Estimated embedding cost: ${report.est_embed_usd:.2f}")
    print(f"Estimated monthly total: ${report.total_usd:.2f}")
    print(f"Configured budget cap: ${max_monthly_usd:.2f}")

    if report.total_usd > max_monthly_usd:
        print("BUDGET CHECK: FAIL")
        return 1

    print("BUDGET CHECK: PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Estimate monthly LLM/embedding costs from DB usage.")
    parser.add_argument("--max-monthly-usd", type=float, default=25.0)
    parser.add_argument("--database-url", default=settings.database_url)
    args = parser.parse_args()
    return asyncio.run(_async_main(args.max_monthly_usd, args.database_url))


if __name__ == "__main__":
    raise SystemExit(main())
