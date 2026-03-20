from backend.agents.llm_client import llm_json_call_with_fallback
from backend.scoring.authority import SOURCE_TYPE_AUTHORITY


async def extract_signals(clean_text: str, entity_id: str, entity_type: str, source_url: str) -> list[dict]:
    prompt = (
        "Read this text and identify any business signals present. "
        "For each signal return: signal_type (one of: hiring/funding/leadership_change/"
        "product_launch/website_change/expansion/layoff/acquisition/other), "
        "description (1 sentence), confidence (0-1), event_date (YYYY-MM-DD or null). "
        "Return JSON with key signals as an array only.\n"
        f"Text:\n{clean_text[:6000]}"
    )
    data = await llm_json_call_with_fallback(prompt)
    rows = data.get("signals", data if isinstance(data, list) else [])

    signals: list[dict] = []
    for row in rows:
        signal_type = str(row.get("signal_type", "other"))
        confidence = max(0.0, min(1.0, float(row.get("confidence", 0.5))))
        authority = SOURCE_TYPE_AUTHORITY.get("unknown", 0.25)
        signals.append(
            {
                "entity_id": entity_id,
                "entity_type": entity_type,
                "signal_type": signal_type,
                "description": str(row.get("description", "")).strip(),
                "confidence": confidence,
                "impact_score": confidence * authority,
                "source_url": source_url,
                "event_date": row.get("event_date"),
            }
        )

    return signals
