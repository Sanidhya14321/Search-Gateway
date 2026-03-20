---
description: Load when implementing retry logic, circuit breakers, graceful degradation, fallback responses, input sanitization, or the exception hierarchy. Auto-loads for utils/retry.py, utils/circuit_breaker.py, utils/sanitize.py, utils/exceptions.py.
applyTo: "{backend/utils/retry.py,backend/utils/circuit_breaker.py,backend/utils/sanitize.py,backend/utils/exceptions.py,backend/agents/llm_client.py,backend/agents/nodes/synthesize.py}"
---

# Error Handling — Quick Reference

Full patterns in: `#file:.agents/skills/error-handling-resilience/SKILL.md`

## 3 Things That Must Exist Before Any LLM Call

1. **`@llm_retry`** decorator on `llm_json_call` — 3 attempts, exponential backoff
2. **`llm_breaker.call(coro, fallback=...)`** wrapping every synthesis call
3. **`wrap_user_input_in_prompt(query, context)`** on every user query before LLM

## Degradation Chain (in order)

```
Full LLM synthesis
  → circuit OPEN? → template_fallback(ranked_chunks)
  → stale cache hit? → cached + stale=true
  → all fail? → {degraded:true, raw_chunks:[...], status:"partial"}
```

Never return HTTP 500 when partial results exist.

## Exception Import

```python
from backend.utils.exceptions import (
    EntityNotFoundError, EntityResolutionError,
    LLMUnavailableError, EmbeddingModelMismatchError,
    RateLimitError, PromptInjectionError,
)
```

## Sanitize Import

```python
from backend.utils.sanitize import sanitize_query, wrap_user_input_in_prompt
```

Call `sanitize_query()` before EVERY LLM prompt. No exceptions.