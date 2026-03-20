def validate_citations(response: dict) -> list[str]:
    warnings: list[str] = []
    for fact in response.get("facts", []):
        if not fact.get("citations"):
            warnings.append(f"Uncited fact: {str(fact.get('claim', ''))[:80]}")

    for person in response.get("people", []):
        name = person.get("full_name") or person.get("name") or "unknown"
        if not person.get("citations"):
            warnings.append(f"Uncited person: {name}")

    return warnings
