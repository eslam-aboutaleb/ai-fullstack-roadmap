"""Coordinated workflow retry policies, circuit breakers, and orchestration cost explosion defense.

Demonstrates:
1. Coordinated retry policy: Distinguishing transient network errors from deterministic validation faults (fail-fast).
2. Exponential backoff with jitter: Preventing thundering herd load spikes on recovering dependencies.
3. Step-level Circuit Breaker state machine (CLOSED -> OPEN -> HALF_OPEN): Halting requests immediately when an upstream service is down.
4. Global task retry budget: Capping total retries across all steps to avoid exponential cost explosions.
"""
from typing import Any, Callable, Dict, Optional, Tuple
import random
import time

class CircuitBreakerOpenException(Exception):
    pass

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_time_seconds: float = 1.0):
        self.threshold = failure_threshold
        self.recovery_time = recovery_time_seconds
        self.failure_count = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.last_failure_time = 0.0

    def record_success(self):
        self.failure_count = 0
        self.state = "CLOSED"

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.threshold:
            self.state = "OPEN"

    def can_execute(self) -> bool:
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_time:
                self.state = "HALF_OPEN"
                return True
            return False
        return True  # HALF_OPEN allows probe request

class CoordinatedRetryOrchestrator:
    def __init__(self, max_total_retries: int = 4):
        self.global_retry_budget = max_total_retries
        self.retries_consumed = 0
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}

    def get_circuit_breaker(self, service_name: str) -> CircuitBreaker:
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreaker()
        return self.circuit_breakers[service_name]

    def execute_with_coordination(
        self,
        service_name: str,
        action: Callable[[], Any],
        max_step_attempts: int = 3
    ) -> Any:
        breaker = self.get_circuit_breaker(service_name)
        if not breaker.can_execute():
            raise CircuitBreakerOpenException(f"Circuit Breaker for '{service_name}' is OPEN. Fast failing request.")

        base_delay = 0.01

        for attempt in range(1, max_step_attempts + 1):
            try:
                result = action()
                breaker.record_success()
                return result

            except ConnectionError as transient_err:
                breaker.record_failure()

                if self.retries_consumed >= self.global_retry_budget:
                    raise RuntimeError("Global workflow retry budget exhausted. Halting execution to prevent cost explosion.")

                if attempt == max_step_attempts:
                    raise

                # Check if breaker opened
                if not breaker.can_execute():
                    raise CircuitBreakerOpenException(f"Circuit Breaker tripped to OPEN on step failure.")

                self.retries_consumed += 1
                # Exponential backoff with jitter
                delay = (base_delay * (2 ** (attempt - 1))) + (random.random() * 0.005)
                time.sleep(delay)

            except (ValueError, KeyError, PermissionError) as deterministic_err:
                # Deterministic business/schema error: NEVER RETRY! Fail immediately.
                raise

def run_tests():
    orch = CoordinatedRetryOrchestrator(max_total_retries=6)

    # 1. Transient recovery with backoff
    attempts = 0
    def flaky_service():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise ConnectionError("503 Gateway Timeout")
        return "service_success"

    res = orch.execute_with_coordination("search_api", flaky_service, max_step_attempts=4)
    assert res == "service_success"
    assert attempts == 3
    assert orch.retries_consumed == 2

    # 2. Deterministic failure fails fast with 0 retries
    det_attempts = 0
    def bad_args_service():
        nonlocal det_attempts
        det_attempts += 1
        raise ValueError("Invalid parameter format")

    try:
        orch.execute_with_coordination("auth_api", bad_args_service)
        assert False, "Should fail fast"
    except ValueError:
        pass
    # Verified: Zero retries wasted on deterministic error!
    assert det_attempts == 1

    # 3. Circuit breaker trips after 3 consecutive failures
    dead_service_calls = 0
    def permanently_dead_service():
        nonlocal dead_service_calls
        dead_service_calls += 1
        raise ConnectionError("Connection Refused")

    try:
        orch.execute_with_coordination("payment_api", permanently_dead_service, max_step_attempts=3)
    except (ConnectionError, CircuitBreakerOpenException):
        pass

    # Subsequent request fast-fails via circuit breaker without touching network!
    breaker = orch.get_circuit_breaker("payment_api")
    assert breaker.state == "OPEN"

    try:
        orch.execute_with_coordination("payment_api", permanently_dead_service)
        assert False, "Should fast-fail due to OPEN breaker"
    except CircuitBreakerOpenException as cbe:
        assert "is OPEN" in str(cbe)

    print("Coordinated retries, circuit breakers, and cost explosion defenses verified successfully.")

if __name__ == "__main__":
    run_tests()
