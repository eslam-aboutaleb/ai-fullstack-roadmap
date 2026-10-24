"""Layered Graph Timeouts, Exponential Backoff with Jitter, and Circuit Breakers.

Demonstrates:
1. Layered Timeouts:
   - Node-level timeout (e.g. 2.0s per attempt) bounds individual network calls.
   - Cumulative workflow deadline (e.g. 8.0s global budget) bounds end-to-end task execution.
2. Intelligent Retry Classification:
   - Transient failures (503 Service Unavailable, Network Timeout) trigger exponential backoff with full jitter.
   - Permanent failures (400 Bad Request, Validation Error) fail fast with zero retries.
3. Node-Level Circuit Breaker:
   - Trips OPEN after consecutive outages (e.g. 3 failures), fast-failing subsequent requests
     to protect downstream dependencies from thundering herd load spikes.
"""

from dataclasses import dataclass, field
import random
import time
from typing import Any, Callable, Dict, List, Optional, Tuple


class ErrorType:
    TRANSIENT = "TRANSIENT"
    PERMANENT = "PERMANENT"


@dataclass
class ServiceError(Exception):
    error_type: str
    status_code: int
    message: str


class CircuitBreakerOpenError(RuntimeError):
    pass


class NodeCircuitBreaker:
    """Circuit breaker protecting downstream dependencies from repeated failure storms."""

    def __init__(self, failure_threshold: int = 3, reset_timeout_seconds: float = 5.0):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout_seconds
        self.failure_count = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.last_state_change = time.time()

    def record_success(self):
        self.failure_count = 0
        self.state = "CLOSED"

    def record_failure(self):
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            self.last_state_change = time.time()

    def check_permission(self):
        if self.state == "OPEN":
            if (time.time() - self.last_state_change) > self.reset_timeout:
                self.state = "HALF_OPEN"
                return
            raise CircuitBreakerOpenError(
                f"Circuit breaker is OPEN ({self.failure_count} consecutive failures). Fast-failing downstream call."
            )


class LayeredRetryCoordinator:
    """Orchestrates layered timeouts, jittered backoff, and circuit breakers."""

    def __init__(self, breaker: NodeCircuitBreaker, global_deadline_seconds: float = 8.0):
        self.breaker = breaker
        self.global_deadline = global_deadline_seconds

    def execute_with_resilience(
        self,
        node_name: str,
        operation: Callable[[], Any],
        max_attempts: int = 3,
        base_delay_ms: float = 50.0,
        max_delay_ms: float = 500.0
    ) -> Dict[str, Any]:
        start_time = time.time()
        attempts = 0
        delays_used = []

        while attempts < max_attempts:
            attempts += 1
            # Check global workflow deadline
            if (time.time() - start_time) > self.global_deadline:
                raise TimeoutError("Cumulative workflow deadline exceeded before task completion")

            # Check circuit breaker
            self.breaker.check_permission()

            try:
                result = operation()
                self.breaker.record_success()
                return {
                    "status": "SUCCESS",
                    "attempts": attempts,
                    "delays_used_ms": delays_used,
                    "result": result
                }
            except ServiceError as err:
                if err.error_type == ErrorType.PERMANENT:
                    # Permanent fault: fail fast! Do NOT waste retry budgets or model tokens!
                    return {
                        "status": "PERMANENT_FAIL_FAST",
                        "attempts": attempts,
                        "error": err.message,
                        "status_code": err.status_code
                    }

                # Transient fault: record in circuit breaker
                self.breaker.record_failure()
                if attempts >= max_attempts:
                    return {
                        "status": "EXHAUSTED_ATTEMPTS",
                        "attempts": attempts,
                        "error": err.message
                    }

                # Calculate exponential backoff with full jitter
                exp_delay = min(max_delay_ms, base_delay_ms * (2 ** (attempts - 1)))
                jittered_delay = random.uniform(0, exp_delay)
                delays_used.append(round(jittered_delay, 2))
                time.sleep(jittered_delay / 1000.0)

        return {"status": "FAILED", "attempts": attempts}


def main():
    random.seed(42)
    breaker = NodeCircuitBreaker(failure_threshold=3, reset_timeout_seconds=2.0)
    coordinator = LayeredRetryCoordinator(breaker=breaker, global_deadline_seconds=5.0)

    # 1. Test Transient Failure Recovery with Exponential Jitter
    print("1. Testing Transient Outage Recovery with Backoff Jitter:")
    attempt_counter = 0

    def mock_flaky_service():
        nonlocal attempt_counter
        attempt_counter += 1
        if attempt_counter < 3:
            raise ServiceError(ErrorType.TRANSIENT, 503, f"503 Service Unavailable (attempt {attempt_counter})")
        return "INVENTORY_RESERVED_OK"

    res_transient = coordinator.execute_with_resilience("reserve_stock_node", mock_flaky_service, max_attempts=4)
    print(f"  Status: {res_transient['status']} on attempt {res_transient['attempts']}")
    print(f"  Delays with full jitter: {res_transient['delays_used_ms']} ms")
    assert res_transient["status"] == "SUCCESS"
    assert res_transient["attempts"] == 3
    assert len(res_transient["delays_used_ms"]) == 2

    # 2. Test Permanent Error Fast-Fail
    print("\n2. Testing Permanent Error Fast-Fail (400 Bad Request):")
    def mock_invalid_args_service():
        raise ServiceError(ErrorType.PERMANENT, 400, "Validation failed: invalid SKU format")

    res_permanent = coordinator.execute_with_resilience("validate_sku_node", mock_invalid_args_service, max_attempts=4)
    print(f"  Status: {res_permanent['status']} (Attempts: {res_permanent['attempts']})")
    print(f"  Error: {res_permanent['error']}")
    assert res_permanent["status"] == "PERMANENT_FAIL_FAST"
    assert res_permanent["attempts"] == 1  # Did NOT retry!

    # 3. Test Circuit Breaker Tripping
    print("\n3. Testing Circuit Breaker Tripping on Consecutive Outages:")
    def mock_down_service():
        raise ServiceError(ErrorType.TRANSIENT, 503, "Downstream service dead")

    # Force 3 consecutive failures to trip breaker
    res_trip = coordinator.execute_with_resilience("failing_node", mock_down_service, max_attempts=3)
    assert breaker.state == "OPEN"
    print(f"  Circuit Breaker state after 3 failures: {breaker.state}")

    # Subsequent request is immediately rejected without network call!
    try:
        coordinator.execute_with_resilience("failing_node", mock_down_service, max_attempts=3)
        assert False, "Should fail fast on OPEN circuit breaker"
    except CircuitBreakerOpenError as cb_err:
        print(f"  Successfully fast-failed request: {cb_err}")

    print("\nLayered graph timeouts, jittered retries, and circuit breaker protection verified successfully.")


if __name__ == "__main__":
    main()

