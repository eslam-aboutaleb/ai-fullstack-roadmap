"""LangChain Middleware, Callback Handlers, Budget Enforcement, and PII Sanitization.

Demonstrates:
1. Cross-Cutting Middleware Architecture:
   - Centralizes token budget accounting, rate limiting, and telemetry outside core business logic.
   - Raises `BudgetExhaustedError` immediately when cumulative tokens exceed allowance.
2. Callback Security and Privacy Boundary:
   - Intercepts prompts and tool observations in `on_llm_start` and `on_tool_end` callbacks.
   - Scrubs credit cards, API keys, and sensitive credentials before telemetry logs are emitted.
3. Separation of Concerns:
   - Middleware handles operational limits; domain services handle object permissions and consistency.
"""

from dataclasses import dataclass, field
import json
import re
from typing import Any, Callable, Dict, List, Optional


class BudgetExhaustedError(RuntimeError):
    pass


@dataclass
class TelemetryEvent:
    event_type: str
    sanitized_payload: Dict[str, Any]


class SecurityAndBudgetMiddleware:
    """Middleware enforcing token budgets and scrubbing PII/credentials from callbacks."""

    CREDENTIAL_PATTERNS = [
        (re.compile(r"\b(sk-[a-zA-Z0-9]{20,})\b"), "[REDACTED_API_KEY]"),
        (re.compile(r"\b(?:\d{4}-){3}\d{4}\b"), "[REDACTED_CREDIT_CARD]"),
        (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[REDACTED_SSN]")
    ]

    def __init__(self, token_budget: int = 1000):
        self.token_budget = token_budget
        self.cumulative_tokens = 0
        self.telemetry_sink: List[TelemetryEvent] = []

    def sanitize_text(self, text: str) -> str:
        sanitized = text
        for pattern, replacement in self.CREDENTIAL_PATTERNS:
            sanitized = pattern.sub(replacement, sanitized)
        return sanitized

    def on_llm_start(self, prompt: str, estimated_tokens: int):
        # 1. Budget enforcement check
        if (self.cumulative_tokens + estimated_tokens) > self.token_budget:
            raise BudgetExhaustedError(
                f"Token budget exhausted! Requested {estimated_tokens} tokens, but remaining allowance is "
                f"{self.token_budget - self.cumulative_tokens} (Total budget: {self.token_budget})"
            )

        self.cumulative_tokens += estimated_tokens

        # 2. Telemetry emission with strict PII scrubbing
        safe_prompt = self.sanitize_text(prompt)
        self.telemetry_sink.append(TelemetryEvent(
            event_type="on_llm_start",
            sanitized_payload={"prompt": safe_prompt, "tokens": estimated_tokens}
        ))

    def on_tool_end(self, tool_name: str, raw_output: str):
        # PII scrubbing on tool observations
        safe_output = self.sanitize_text(raw_output)
        self.telemetry_sink.append(TelemetryEvent(
            event_type="on_tool_end",
            sanitized_payload={"tool": tool_name, "observation": safe_output}
        ))


class MonitoredChainRunner:
    """Executes chain turns monitored by the security middleware."""

    def __init__(self, middleware: SecurityAndBudgetMiddleware):
        self.middleware = middleware

    def run_step(self, prompt: str, tokens: int, tool_output: Optional[str] = None) -> str:
        # Trigger on_llm_start
        self.middleware.on_llm_start(prompt, estimated_tokens=tokens)

        # Trigger on_tool_end if tool ran
        if tool_output:
            self.middleware.on_tool_end("customer_lookup", tool_output)

        return f"Completed turn using {tokens} tokens."


def main():
    middleware = SecurityAndBudgetMiddleware(token_budget=500)
    runner = MonitoredChainRunner(middleware)

    # 1. Execute Turn 1 with sensitive API key and credit card in prompt
    print("1. Running Turn with Sensitive Credentials:")
    dirty_prompt = "Query customer profile with sk-99881122334455667788 and card 4111-2222-3333-4444"
    dirty_observation = "Customer SSN is 000-12-3456; account in good standing."

    reply1 = runner.run_step(dirty_prompt, tokens=200, tool_output=dirty_observation)
    print(f"  Step 1 Result: {reply1}")
    print(f"  Cumulative Tokens: {middleware.cumulative_tokens}/{middleware.token_budget}")

    # Inspect Telemetry Sink to verify sanitization
    print("\n2. Verifying Callback Telemetry Sanitization:")
    llm_event = middleware.telemetry_sink[0]
    tool_event = middleware.telemetry_sink[1]

    print(f"  Sanitized Prompt: '{llm_event.sanitized_payload['prompt']}'")
    print(f"  Sanitized Tool Obs: '{tool_event.sanitized_payload['observation']}'")

    assert "sk-" not in llm_event.sanitized_payload["prompt"]
    assert "[REDACTED_API_KEY]" in llm_event.sanitized_payload["prompt"]
    assert "[REDACTED_CREDIT_CARD]" in llm_event.sanitized_payload["prompt"]
    assert "000-12-3456" not in tool_event.sanitized_payload["observation"]
    assert "[REDACTED_SSN]" in tool_event.sanitized_payload["observation"]

    # 2. Execute Turn 2 (within budget)
    reply2 = runner.run_step("Second turn inquiry", tokens=200)
    print(f"\n3. Step 2 Result: {reply2} (Tokens: {middleware.cumulative_tokens}/{middleware.token_budget})")
    assert middleware.cumulative_tokens == 400

    # 3. Execute Turn 3 exceeding remaining budget (400 + 200 > 500)
    print("\n4. Testing Token Budget Exhaustion Invariant:")
    try:
        runner.run_step("Third turn demanding 200 tokens", tokens=200)
        assert False, "Execution must be aborted when exceeding token budget"
    except BudgetExhaustedError as err:
        print(f"  Successfully blocked turn exceeding budget: {err}")
        assert "Token budget exhausted!" in str(err)

    print("\nMiddleware budget guardrails, callback interception, and PII sanitization verified successfully.")


if __name__ == "__main__":
    main()

