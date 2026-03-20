class CRMindError(Exception):
    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"

    def __init__(self, message: str = "Internal server error"):
        super().__init__(message)


class EntityNotFoundError(CRMindError):
    status_code = 404
    error_code = "ENTITY_NOT_FOUND"


class EntityResolutionError(CRMindError):
    status_code = 422
    error_code = "ENTITY_RESOLUTION_FAILED"


class LLMUnavailableError(CRMindError):
    status_code = 503
    error_code = "LLM_UNAVAILABLE"


class EmbeddingModelMismatchError(CRMindError):
    status_code = 500
    error_code = "EMBEDDING_MODEL_MISMATCH"


class RateLimitError(CRMindError):
    status_code = 429
    error_code = "RATE_LIMIT_EXCEEDED"


class PromptInjectionError(CRMindError):
    status_code = 400
    error_code = "PROMPT_INJECTION_DETECTED"
