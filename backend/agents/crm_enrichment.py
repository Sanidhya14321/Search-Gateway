import asyncio

from backend.agents.graph_runtime import END, START, StateGraph

from backend.agents.state import CRMindState
from backend.database import get_pool
from backend.database import resolve_pool
from backend.services.entity_resolver import resolve_entity


async def validate_input_node(state: CRMindState) -> dict:
    leads = state.get("lead_list", [])
    if not leads:
        return {"error": "lead_list is required", "steps_log": state.get("steps_log", []) + ["[validate_input] no leads"]}
    return {"steps_log": state.get("steps_log", []) + [f"[validate_input] leads={len(leads)}"]}


async def batch_resolve_node(state: CRMindState) -> dict:
    leads = state.get("lead_list", [])
    semaphore = asyncio.Semaphore(10)

    async def _resolve(lead: dict) -> dict:
        async with semaphore:
            entity = await resolve_entity(str(lead.get("company", "")))
            return {
                "lead": lead,
                "resolved": entity.record if entity else None,
                "confidence": entity.confidence if entity else 0.0,
            }

    resolved = await asyncio.gather(*[_resolve(lead) for lead in leads])
    return {"resolved_batch": resolved, "steps_log": state.get("steps_log", []) + ["[batch_resolve] complete"]}


async def check_existing_node(state: CRMindState) -> dict:
    resolved_batch = state.get("resolved_batch", [])
    pool = await resolve_pool(get_pool())
    to_enrich = []
    skipped_fresh = 0

    async with pool.acquire() as db:
        for row in resolved_batch:
            resolved = row.get("resolved")
            if not resolved:
                to_enrich.append(row)
                continue

            freshness = await db.fetchval("SELECT freshness_score FROM companies WHERE id=$1::uuid", resolved["id"])
            if freshness is not None and float(freshness) > 0.7:
                skipped_fresh += 1
            else:
                to_enrich.append(row)

    return {
        "to_enrich": to_enrich,
        "skipped_fresh": skipped_fresh,
        "steps_log": state.get("steps_log", []) + [f"[check_existing] to_enrich={len(to_enrich)} skipped={skipped_fresh}"],
    }


async def enrich_missing_node(state: CRMindState) -> dict:
    enriched = []
    for row in state.get("to_enrich", []):
        lead = row["lead"]
        enriched.append(
            {
                "company": lead.get("company"),
                "full_name": lead.get("name", ""),
                "title": lead.get("title"),
                "email": lead.get("email"),
                "confidence": row.get("confidence", 0.0),
            }
        )
    return {"enriched_rows": enriched, "steps_log": state.get("steps_log", []) + [f"[enrich_missing] enriched={len(enriched)}"]}


async def flag_low_confidence_node(state: CRMindState) -> dict:
    flagged = [row for row in state.get("enriched_rows", []) if float(row.get("confidence", 0.0)) < 0.6]
    return {
        "flagged_low_confidence": flagged,
        "steps_log": state.get("steps_log", []) + [f"[flag_low_confidence] flagged={len(flagged)}"],
    }


async def deduplicate_batch_node(state: CRMindState) -> dict:
    deduped: dict[str, dict] = {}
    for row in state.get("enriched_rows", []):
        key = f"{row.get('full_name', '').lower()}::{row.get('company', '').lower()}"
        deduped[key] = row
    return {"deduped_rows": list(deduped.values()), "steps_log": state.get("steps_log", []) + ["[deduplicate_batch] complete"]}


async def write_back_node(state: CRMindState) -> dict:
    rows = state.get("deduped_rows", [])
    if not rows:
        return {"write_back_count": 0, "steps_log": state.get("steps_log", []) + ["[write_back] nothing to persist"]}

    pool = await resolve_pool(get_pool())
    async with pool.acquire() as db:
        for row in rows:
            company_name = str(row.get("company", "")).strip() or "Unknown"
            company_id = await db.fetchval(
                """
                INSERT INTO companies (canonical_id, canonical_name)
                VALUES ($1, $2)
                ON CONFLICT (canonical_id) DO UPDATE SET canonical_name=EXCLUDED.canonical_name
                RETURNING id
                """,
                f"comp_{company_name.lower().replace(' ', '_')}",
                company_name,
            )
            full_name = str(row.get("full_name", "Unknown"))
            person_canonical_id = f"pers_{full_name.lower().replace(' ', '_')}_{str(company_id)[:8]}"
            await db.execute(
                """
                INSERT INTO people (canonical_id, full_name, current_title, current_company_id)
                VALUES ($1, $2, $3, $4::uuid)
                ON CONFLICT (canonical_id) DO UPDATE
                SET full_name=EXCLUDED.full_name,
                    current_title=EXCLUDED.current_title,
                    current_company_id=EXCLUDED.current_company_id,
                    updated_at=NOW()
                """,
                person_canonical_id,
                full_name,
                row.get("title"),
                company_id,
            )

    return {"write_back_count": len(rows), "steps_log": state.get("steps_log", []) + [f"[write_back] rows={len(rows)}"]}


async def generate_report_node(state: CRMindState) -> dict:
    total = len(state.get("lead_list", []))
    enriched = int(state.get("write_back_count", 0))
    skipped_fresh = int(state.get("skipped_fresh", 0))
    flagged = len(state.get("flagged_low_confidence", []))
    failed = max(total - (enriched + skipped_fresh), 0)
    report = {
        "total": total,
        "enriched": enriched,
        "skipped_fresh": skipped_fresh,
        "flagged_low_confidence": flagged,
        "failed": failed,
        "fields_added": ["company", "full_name", "title"],
        "warnings": ["Some rows were low-confidence"] if flagged else [],
    }
    return {
        "final_response": report,
        "steps_log": state.get("steps_log", []) + ["[generate_report] complete"],
    }


def build_crm_enrichment_graph():
    graph = StateGraph(CRMindState)
    graph.add_node("validate_input", validate_input_node)
    graph.add_node("batch_resolve", batch_resolve_node)
    graph.add_node("check_existing", check_existing_node)
    graph.add_node("enrich_missing", enrich_missing_node)
    graph.add_node("flag_low_confidence", flag_low_confidence_node)
    graph.add_node("deduplicate_batch", deduplicate_batch_node)
    graph.add_node("write_back", write_back_node)
    graph.add_node("generate_report", generate_report_node)

    graph.add_edge(START, "validate_input")
    graph.add_edge("validate_input", "batch_resolve")
    graph.add_edge("batch_resolve", "check_existing")
    graph.add_edge("check_existing", "enrich_missing")
    graph.add_edge("enrich_missing", "flag_low_confidence")
    graph.add_edge("flag_low_confidence", "deduplicate_batch")
    graph.add_edge("deduplicate_batch", "write_back")
    graph.add_edge("write_back", "generate_report")
    graph.add_edge("generate_report", END)
    return graph.compile()
