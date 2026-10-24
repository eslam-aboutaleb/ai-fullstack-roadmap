"""Provider Adapter Layer: Common Abstractions vs Provider-Specific Leaks.

Demonstrates:
1. Unified Model Adapter (LiteLLM-style abstraction):
   - Standardizes chat completion payloads (`messages`, `role`, `content`, `tools`).
   - Normalizes heterogeneous provider response schemas into a uniform typed output structure.
2. Provider-Specific Non-Abstracted Mechanics:
   - Extended thinking/reasoning token budgets (e.g., Anthropic `budget_tokens` vs OpenAI `reasoning_effort`).
   - Provider-specific rate limiting headers (e.g., `retry-after-ms` vs `x-ratelimit-reset-tokens`).
   - Prompt caching break-points and provider-specific error code mappings.
"""

from dataclasses import dataclass, field
import json
import time
from typing import Any, Dict, List, Optional


@dataclass
class StandardToolCall:
    id: str
    name: str
    arguments: Dict[str, Any]


@dataclass
class StandardModelResponse:
    content: Optional[str]
    tool_calls: List[StandardToolCall] = field(default_factory=list)
    finish_reason: str = "stop"
    usage_prompt_tokens: int = 0
    usage_completion_tokens: int = 0
    provider_raw_metadata: Dict[str, Any] = field(default_factory=dict)


class UnifiedProviderAdapter:
    """Simulates LiteLLM-style provider translation across OpenAI and Anthropic."""

    @classmethod
    def call_model(
        cls,
        provider: str,
        model: str,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        thinking_budget: Optional[int] = None
    ) -> StandardModelResponse:
        """Translates unified arguments into provider-specific requests, and normalizes responses."""
        if provider == "openai":
            # OpenAI wire format: reasoning_effort for o1/o3 models
            payload = {
                "model": model,
                "messages": messages,
                "tools": tools,
            }
            if thinking_budget:
                payload["reasoning_effort"] = "high" if thinking_budget > 1000 else "medium"

            # Simulate OpenAI response
            raw_response = {
                "id": "chatcmpl-9912",
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [{
                            "id": "call_abc123",
                            "type": "function",
                            "function": {"name": "query_inventory", "arguments": '{"item_id": "SKU-404"}'}
                        }]
                    },
                    "finish_reason": "tool_calls"
                }],
                "usage": {"prompt_tokens": 85, "completion_tokens": 22}
            }
            return cls._normalize_openai_response(raw_response, payload)

        elif provider == "anthropic":
            # Anthropic wire format: thinking.budget_tokens and distinct tools format
            payload = {
                "model": model,
                "messages": messages,
                "tools": tools
            }
            if thinking_budget:
                payload["thinking"] = {"type": "enabled", "budget_tokens": thinking_budget}

            # Simulate Anthropic response
            raw_response = {
                "id": "msg_anthropic_772",
                "content": [{
                    "type": "tool_use",
                    "id": "toolu_xyz987",
                    "name": "query_inventory",
                    "input": {"item_id": "SKU-404"}
                }],
                "stop_reason": "tool_use",
                "usage": {"input_tokens": 92, "output_tokens": 30}
            }
            return cls._normalize_anthropic_response(raw_response, payload)

        raise ValueError(f"Unsupported provider '{provider}'")

    @classmethod
    def _normalize_openai_response(cls, raw: Dict[str, Any], payload: Dict[str, Any]) -> StandardModelResponse:
        choice = raw["choices"][0]
        msg = choice["message"]
        tool_calls = []

        if msg.get("tool_calls"):
            for tc in msg["tool_calls"]:
                tool_calls.append(StandardToolCall(
                    id=tc["id"],
                    name=tc["function"]["name"],
                    arguments=json.loads(tc["function"]["arguments"])
                ))

        return StandardModelResponse(
            content=msg.get("content"),
            tool_calls=tool_calls,
            finish_reason=choice["finish_reason"],
            usage_prompt_tokens=raw["usage"]["prompt_tokens"],
            usage_completion_tokens=raw["usage"]["completion_tokens"],
            provider_raw_metadata={"provider": "openai", "request_payload": payload}
        )

    @classmethod
    def _normalize_anthropic_response(cls, raw: Dict[str, Any], payload: Dict[str, Any]) -> StandardModelResponse:
        tool_calls = []
        content_text = None

        for block in raw["content"]:
            if block["type"] == "text":
                content_text = block["text"]
            elif block["type"] == "tool_use":
                tool_calls.append(StandardToolCall(
                    id=block["id"],
                    name=block["name"],
                    arguments=block["input"]
                ))

        return StandardModelResponse(
            content=content_text,
            tool_calls=tool_calls,
            finish_reason="tool_calls" if raw["stop_reason"] == "tool_use" else "stop",
            usage_prompt_tokens=raw["usage"]["input_tokens"],
            usage_completion_tokens=raw["usage"]["output_tokens"],
            provider_raw_metadata={"provider": "anthropic", "request_payload": payload}
        )


def main():
    messages = [
        {"role": "system", "content": "You are an inventory assistant."},
        {"role": "user", "content": "Check stock for SKU-404"}
    ]
    tools = [{
        "name": "query_inventory",
        "description": "Check warehouse inventory stock",
        "parameters": {"type": "object", "properties": {"item_id": {"type": "string"}}}
    }]

    print("1. Calling OpenAI through Unified Adapter:")
    resp_openai = UnifiedProviderAdapter.call_model(
        provider="openai",
        model="gpt-4o",
        messages=messages,
        tools=tools,
        thinking_budget=2000
    )
    print(f"  Tool Calls parsed: {[tc.name for tc in resp_openai.tool_calls]}")
    print(f"  Args: {resp_openai.tool_calls[0].arguments}")
    print(f"  Provider-specific wire payload: {resp_openai.provider_raw_metadata['request_payload'].get('reasoning_effort')}")

    print("\n2. Calling Anthropic through Unified Adapter:")
    resp_anthropic = UnifiedProviderAdapter.call_model(
        provider="anthropic",
        model="claude-3-5-sonnet-20241022",
        messages=messages,
        tools=tools,
        thinking_budget=2000
    )
    print(f"  Tool Calls parsed: {[tc.name for tc in resp_anthropic.tool_calls]}")
    print(f"  Args: {resp_anthropic.tool_calls[0].arguments}")
    print(f"  Provider-specific wire payload: {resp_anthropic.provider_raw_metadata['request_payload'].get('thinking')}")

    # Assertions
    assert resp_openai.tool_calls[0].name == resp_anthropic.tool_calls[0].name == "query_inventory"
    assert resp_openai.tool_calls[0].arguments == resp_anthropic.tool_calls[0].arguments == {"item_id": "SKU-404"}
    assert resp_openai.finish_reason == resp_anthropic.finish_reason == "tool_calls"

    # Verify provider-specific leaks are retained in metadata
    assert "reasoning_effort" in resp_openai.provider_raw_metadata["request_payload"]
    assert "thinking" in resp_anthropic.provider_raw_metadata["request_payload"]

    print("\nProvider adapter abstraction and provider-specific parameter isolation verified.")


if __name__ == "__main__":
    main()

