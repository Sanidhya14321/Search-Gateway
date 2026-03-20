import asyncio
import time
from enum import Enum


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self._failures = 0
        self._state = CircuitState.CLOSED
        self._opened_at: float | None = None

    def _can_try_recovery(self) -> bool:
        if self._opened_at is None:
            return True
        return (time.time() - self._opened_at) > self.recovery_timeout

    def _on_success(self) -> None:
        self._failures = 0
        self._state = CircuitState.CLOSED
        self._opened_at = None

    def _on_failure(self) -> None:
        self._failures += 1
        if self._failures >= self.failure_threshold or self._state == CircuitState.HALF_OPEN:
            self._state = CircuitState.OPEN
            self._opened_at = time.time()

    async def call(self, coro, fallback=None):
        if self._state == CircuitState.OPEN:
            if self._can_try_recovery():
                self._state = CircuitState.HALF_OPEN
            else:
                if fallback is not None:
                    if asyncio.iscoroutinefunction(fallback):
                        return await fallback()
                    return fallback()
                raise RuntimeError("Circuit breaker OPEN")

        try:
            result = await coro
            self._on_success()
            return result
        except Exception:
            self._on_failure()
            raise


llm_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60)
embed_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=30)
