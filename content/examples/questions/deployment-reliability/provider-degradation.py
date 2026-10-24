"""Provider Degradation, Circuit Breaking, and Declared Fallback.

Demonstrates resilient handling of upstream LLM provider degradation.
Implements a 3-state circuit breaker (Closed, Open, Half-Open) that fast-fails
during provider outages, returning honest declared degradation envelopes.
"""

from dataclasses import dataclass, field
from enum import Enum
import time
from typing import Any, Dict, List, Optional, Tuple


class CircuitState(str, Enum):
    CLOSED = "closed"  # Normal healthy operation
    OPEN = "open"  # Fast-failing; provider degraded
    HALF_OPEN = "half_open"  # Testing canary requests


@dataclass
class ProviderResponseEnvelope:
    status: str  # "ok", "temporarily_unavailable", "cached_fallback"
    data: Optional[str] = None
    retry_after_seconds: Optional[int] = None
    circuit_state: str = "closed"


class ProviderCircuitBreaker:
    """Protects application concurrency during upstream API provider failures."""

    def __init__(
        self, failure_threshold: int = 3, recovery_timeout_sec: float = 30.0
    ) -> None:
        self.failure_threshold = failure_threshold
        self.recovery_timeout_sec = recovery_timeout_sec
        self.state: CircuitState = CircuitState.CLOSED
        self.consecutive_failures: int = 0
        self.last_state_change_time: float = time.time()
        self.cached_fallback_db: Dict[str, str] = {
            "help_policy": "Returns and refunds require proof of purchase within 30 days."
        }

    def record_success(self) -> None:
        self.consecutive_failures = 0
        self.state = CircuitState.CLOSED

    def record_failure(self, current_time: Optional[float] = None) -> None:
        now = current_time if current_time is not None else time.time()
        self.consecutive_failures += 1
        if self.consecutive_failures >= self.failure_threshold:
            self.state = CircuitState.OPEN
            self.last_state_change_time = now

    def execute_query(
        self, prompt_key: str, provider_healthy: bool, simulated_time: Optional[float] = None
    ) -> ProviderResponseEnvelope:
        now = simulated_time if simulated_time is not None else time.time()

        # Check if circuit should transition from OPEN to HALF_OPEN
        if self.state == CircuitState.OPEN:
            if now - self.last_state_change_time >= self.recovery_timeout_sec:
                self.state = CircuitState.HALF_OPEN
            else:
                # Fast-fail immediately! Do not hang or wait on slow provider.
                fallback = self.cached_fallback_db.get(prompt_key)
                return ProviderResponseEnvelope(
                    status="cached_fallback" if fallback else "temporarily_unavailable",
                    data=fallback,
                    retry_after_seconds=int(self.recovery_timeout_sec - (now - self.last_state_change_time)),
                    circuit_state=self.state.value,
                )

        # Attempt call to provider
        if not provider_healthy:
            self.record_failure(current_time=now)
            fallback = self.cached_fallback_db.get(prompt_key)
            return ProviderResponseEnvelope(
                status="cached_fallback" if fallback else "temporarily_unavailable",
                data=fallback,
                retry_after_seconds=30,
                circuit_state=self.state.value,
            )

        # Provider call succeeded
        self.record_success()
        return ProviderResponseEnvelope(
            status="ok",
            data=f"Fresh LLM answer for {prompt_key}",
            circuit_state=self.state.value,
        )


def test_provider_degradation() -> None:
    breaker = ProviderCircuitBreaker(failure_threshold=3, recovery_timeout_sec=30.0)
    assert breaker.state == CircuitState.CLOSED

    # 1. Normal healthy call
    res_healthy = breaker.execute_query("help_policy", provider_healthy=True, simulated_time=100.0)
    assert res_healthy.status == "ok"
    assert "Fresh LLM answer" in res_healthy.data

    # 2. Provider suffers outage: 3 consecutive failures trip the breaker
    breaker.execute_query("custom_calc", provider_healthy=False, simulated_time=101.0)
    breaker.execute_query("custom_calc", provider_healthy=False, simulated_time=102.0)
    res_trip = breaker.execute_query("custom_calc", provider_healthy=False, simulated_time=103.0)

    # Invariant: Circuit is now OPEN
    assert breaker.state == CircuitState.OPEN
    assert res_trip.status == "temporarily_unavailable"

    # 3. Subsequent call at t=105s fast-fails without hitting provider!
    # Returns cached fallback for known prompt
    res_fast_fail = breaker.execute_query("help_policy", provider_healthy=False, simulated_time=105.0)
    assert res_fast_fail.status == "cached_fallback"
    assert "Returns and refunds" in res_fast_fail.data
    assert res_fast_fail.circuit_state == "open"

    # 4. At t=135s (32s later), recovery timeout has elapsed -> Circuit transitions to HALF_OPEN
    # Provider has recovered!
    res_recovered = breaker.execute_query("help_policy", provider_healthy=True, simulated_time=135.0)
    assert res_recovered.status == "ok"
    assert breaker.state == CircuitState.CLOSED

    print(
        f"Provider degradation circuit breaker verified: initial_state=closed, "
        f"tripped_to_open=True, fast_failed_cached=True, recovered_to_closed=True"
    )


if __name__ == "__main__":
    test_provider_degradation()
