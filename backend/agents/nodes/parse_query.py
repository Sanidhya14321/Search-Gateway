from backend.agents import llm_client
from backend.agents.state import CRMindState

async def llm_json_call(prompt: str, system: str = "", model=None):
    # Keep an indirection so tests can patch either this symbol or llm_client.
    return await llm_client.llm_json_call_with_fallback(prompt, system=system, model=model)


async def parse_query_node(state: CRMindState) -> dict:
    prompt = (
        "Extract from the query as JSON with keys: "
        "company_name (string or null), title_keywords (array of strings), "
        "seniority (one of: intern,junior,mid,senior,staff,principal,director,vp,c_level,founder,unknown).\n"
        f"Query: {state.get('query', '')}"
    )
    parsed = await llm_json_call(prompt)
    return {
        "_parsed_filters": parsed,
        "steps_log": state.get("steps_log", []) + ["[parse_query] extracted filters"],
    }
