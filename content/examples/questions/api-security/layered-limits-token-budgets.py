"""Layered limits: Request payload boundaries, sliding-window rate limiters, and agent tool execution budgets.

Demonstrates:
1. Tier 1: Pre-parsing request-size limits (rejecting oversized payloads before JSON memory allocation).
2. Tier 2: Token-bucket rate limiting per caller IP/tenant, smoothing traffic bursts and shedding excess load with 429.
3. Tier 3: Agent execution budget limits, capping total tool invocations per session to prevent infinite LLM loops and runaway costs.
"""
from typing import Any, Dict, List, Optional, Tuple
import time

class TokenBucketRateLimiter:
    def __init__(self, capacity: float, refill_rate_per_sec: float):
        self.capacity = capacity
        self.refill_rate = refill_rate_per_sec
        # client_id -> (tokens, last_refill_time)
        self._buckets: Dict[str, Tuple[float, float]] = {}

    def allow_request(self, client_id: str, cost: float = 1.0) -> bool:
        now = time.time()
        if client_id not in self._buckets:
            self._buckets[client_id] = (self.capacity, now)

        tokens, last_refill = self._buckets[client_id]
        # Calculate refilled tokens
        elapsed = now - last_refill
        tokens = min(self.capacity, tokens + (elapsed * self.refill_rate))

        if tokens >= cost:
            self._buckets[client_id] = (tokens - cost, now)
            return True
        else:
            self._buckets[client_id] = (tokens, now)
            return False

class AgentExecutionBudget:
    def __init__(self, max_tool_invocations: int = 5, max_total_tokens: int = 4000):
        self.max_tools = max_tool_invocations
        self.max_tokens = max_total_tokens
        self.consumed_tools = 0
        self.consumed_tokens = 0

    def consume_tool_call(self, estimated_tokens: int) -> None:
        if self.consumed_tools + 1 > self.max_tools:
            raise RuntimeError(f"Tool budget exhausted: Exceeded maximum {self.max_tools} tool calls per turn.")
        if self.consumed_tokens + estimated_tokens > self.max_tokens:
            raise RuntimeError(f"Token budget exhausted: Exceeded maximum {self.max_tokens} context tokens.")

        self.consumed_tools += 1
        self.consumed_tokens += estimated_tokens

class LayeredProtectionGateway:
    MAX_PAYLOAD_BYTES = 500_000  # 500 KB limit

    def __init__(self):
        self.rate_limiter = TokenBucketRateLimiter(capacity=3.0, refill_rate_per_sec=1.0)

    def process_incoming_request(
        self,
        client_id: str,
        raw_payload_bytes: bytes,
        agent_budget: AgentExecutionBudget
    ) -> Tuple[int, str]:
        # Layer 1: Request size limit check (pre-flight before memory allocation)
        if len(raw_payload_bytes) > self.MAX_PAYLOAD_BYTES:
            return 413, "Payload Too Large: Exceeds 500KB limit."

        # Layer 2: Network rate limiter check
        if not self.rate_limiter.allow_request(client_id):
            return 429, "Too Many Requests: Rate limit exceeded. Retry later."

        # Layer 3: Agent tool execution budget
        try:
            agent_budget.consume_tool_call(estimated_tokens=500)
        except RuntimeError as budget_err:
            return 429, f"Agent Budget Error: {str(budget_err)}"

        return 200, "Request accepted and executed."

if __name__ == "__main__":
    gateway = LayeredProtectionGateway()
    budget = AgentExecutionBudget(max_tool_invocations=3, max_total_tokens=2000)

    # 1. Successful request passing all three tiers
    status1, msg1 = gateway.process_incoming_request("tenant_alpha", b"small payload", budget)
    assert status1 == 200
    assert budget.consumed_tools == 1

    # 2. Layer 1 rejection: Oversized payload rejected with 413
    huge_payload = b"X" * 600_000
    status_huge, msg_huge = gateway.process_incoming_request("tenant_alpha", huge_payload, budget)
    assert status_huge == 413
    assert "Payload Too Large" in msg_huge

    # 3. Layer 2 rejection: Rapid bursts exceed rate limiter bucket (429)
    # Drain remaining tokens
    gateway.process_incoming_request("tenant_alpha", b"ok", budget)
    gateway.process_incoming_request("tenant_alpha", b"ok", budget)
    status_rate, msg_rate = gateway.process_incoming_request("tenant_alpha", b"ok", budget)
    assert status_rate == 429
    assert "Rate limit exceeded" in msg_rate

    # 4. Layer 3 rejection: Agent infinite loop prevented by tool budget
    budget_tight = AgentExecutionBudget(max_tool_invocations=2, max_total_tokens=1000)
    budget_tight.consume_tool_call(300)
    budget_tight.consume_tool_call(300)
    try:
        budget_tight.consume_tool_call(300)
        assert False, "Should raise tool budget exhausted"
    except RuntimeError as e:
        assert "Tool budget exhausted" in str(e)

    print("Layered limits: Request sizes, rate limits, and agent tool budgets verified successfully.")

