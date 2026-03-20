import json

from groq import AsyncGroq
from loguru import logger

from backend.config import settings
from backend.middleware.trace import get_trace_id
from backend.utils.retry import llm_retry
from backend.utils.sanitize import wrap_user_input_in_prompt


def _strip_json_fences(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        parts = cleaned.split("```")
        if len(parts) >= 2:
            cleaned = parts[1]
    if cleaned.startswith("json"):
        cleaned = cleaned[4:]
    return cleaned.strip().rstrip("```").strip()


def _extract_text(content: object) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(str(item.get("text", "")))
        return "\n".join(part for part in parts if part)
    return str(content or "")


def _groq_client() -> AsyncGroq:
    return AsyncGroq(api_key=settings.groq_api_key)


@llm_retry
async def _llm_json_call_groq(prompt: str, system: str = "", model: str | None = None) -> dict:
    safe_prompt = wrap_user_input_in_prompt(prompt, context="Agent workflow context")
    response = await _groq_client().chat.completions.create(
        model=model or settings.groq_llm_model,
        response_format={"type": "json_object"},
        temperature=0,
        messages=[
            {"role": "system", "content": system or "Return valid JSON only."},
            {"role": "user", "content": safe_prompt},
        ],
    )
    raw_text = _extract_text(response.choices[0].message.content)
    try:
        return json.loads(_strip_json_fences(raw_text))
    except Exception as exc:
        logger.error("llm_json_parse_failed | provider=groq trace_id={} error={} raw={}", get_trace_id(), type(exc).__name__, raw_text)
        raise ValueError(raw_text) from exc


@llm_retry
async def llm_json_call(prompt: str, system: str = "", model: str | None = None, provider: str = "groq") -> dict:
    target_provider = provider.lower()
    if target_provider != "groq":
        raise ValueError(f"Unsupported provider: {provider}. This deployment is Groq-only.")
    return await _llm_json_call_groq(prompt=prompt, system=system, model=model)


async def llm_json_call_with_fallback(prompt: str, system: str = "", model: str | None = None) -> dict:
    try:
        return await llm_json_call(prompt=prompt, system=system, model=model or settings.groq_llm_model, provider="groq")
    except Exception as primary_exc:
        logger.warning(
            "llm_primary_failed | trace_id={} error={} fallback_provider=groq_fallback",
            get_trace_id(),
            type(primary_exc).__name__,
        )
        try:
            return await llm_json_call(
                prompt=prompt,
                system=system,
                model=settings.groq_llm_model_fallback,
                provider="groq",
            )
        except Exception as fallback_exc:
            logger.warning(
                "llm_secondary_failed | trace_id={} error={} fallback_provider=none",
                get_trace_id(),
                type(fallback_exc).__name__,
            )
            raise fallback_exc
