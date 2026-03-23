import re

from backend.agents import llm_client
from backend.agents.state import CRMindState

async def llm_json_call(prompt: str, system: str = "", model=None):
    # Keep an indirection so tests can patch either this symbol or llm_client.
    return await llm_client.llm_json_call_with_fallback(prompt, system=system, model=model)


async def parse_query_node(state: CRMindState) -> dict:
    query_text = state.get("query", "")
    prompt = (
        "Extract from the query as JSON with keys: "
        "company_name (string or null), title_keywords (array of strings), "
        "seniority (one of: intern,junior,mid,senior,staff,principal,director,vp,c_level,founder,unknown).\n"
        f"Query: {query_text}"
    )
    try:
        parsed = await llm_json_call(prompt)
    except Exception:
        company_name = None
        lowered = query_text.lower()
        match = re.search(r"\bat\s+([A-Za-z0-9&.,'\- ]+)$", query_text.strip(), flags=re.IGNORECASE)
        if match:
            company_name = match.group(1).strip(" .,")
        title_keywords: list[str] = []
        for keyword in ["engineer", "engineering", "developer", "architect", "data", "backend", "frontend"]:
            if keyword in lowered:
                title_keywords.append(keyword)

        seniority = "unknown"
        if "senior" in lowered or "staff" in lowered or "principal" in lowered:
            seniority = "senior"

        parsed = {
            "company_name": company_name,
            "title_keywords": title_keywords,
            "seniority": seniority,
        }

    return {
        "_parsed_filters": parsed,
        "steps_log": state.get("steps_log", []) + ["[parse_query] extracted filters"],
    }
