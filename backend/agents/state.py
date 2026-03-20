from typing import Any, TypedDict


class CRMindState(TypedDict, total=False):
    query: str
    entity_id: str | None
    entity_type: str | None
    lead_list: list[dict[str, Any]]

    resolved_entity: dict[str, Any] | None
    resolution_confidence: float

    retrieved_chunks: list[dict[str, Any]]
    ranked_chunks: list[dict[str, Any]]
    db_people_results: list[dict[str, Any]]

    tool_calls: list[dict[str, Any]]
    steps_log: list[str]
    iteration_count: int

    final_response: dict[str, Any] | None
    citations: list[dict[str, Any]]
    error: str | None
    cache_hit: bool

    _parsed_filters: dict[str, Any]
    _sub_questions: list[str]
