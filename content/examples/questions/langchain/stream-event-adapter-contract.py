"""Stream Event Adapter, Client Contract Decoupling, and Output Validation.

Demonstrates:
1. Internal Framework Event Decoupling:
   - Framework produces granular internal events (`on_chat_model_stream`, `on_tool_start`, `on_tool_end`).
   - The adapter translates them into application-standard Server-Sent Events (SSE) contracts.
2. Sensitive Data & Implementation Filtering:
   - Strips internal system prompts, model temperatures, private database connection strings,
     and framework class names before streaming to browser clients.
3. Output Schema Validation:
   - Validates generated final structured data against expected Pydantic schemas before emitting
     completion events, preventing malformed payloads from breaking client UI state.
"""

from dataclasses import dataclass, field
import json
from typing import Any, Dict, Generator, List, Optional, Tuple


@dataclass
class InternalFrameworkEvent:
    event_type: str  # e.g., "on_chat_model_start", "on_chat_model_stream", "on_tool_start", "on_tool_end"
    payload: Dict[str, Any]
    internal_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PublicClientEvent:
    event: str  # "token_delta", "tool_status", "final_answer", "error"
    data: Dict[str, Any]

    def to_sse_frame(self) -> str:
        return f"event: {self.event}\ndata: {json.dumps(self.data)}\n\n"


class FrontendStreamAdapter:
    """Translates internal framework events into stable public SSE client envelopes."""

    ALLOWED_PUBLIC_TOOLS = {"search_kb", "check_weather"}

    @classmethod
    def transform_event_stream(
        cls,
        event_stream: List[InternalFrameworkEvent]
    ) -> Generator[PublicClientEvent, None, None]:
        accumulated_text = []

        for internal_evt in event_stream:
            # 1. Internal model start: Strip private system prompt and hyperparameters!
            if internal_evt.event_type == "on_chat_model_start":
                # Do NOT emit private system prompt or internal model hyperparameters to public clients!
                continue

            # 2. Token streaming: Emit clean public token delta
            elif internal_evt.event_type == "on_chat_model_stream":
                chunk = internal_evt.payload.get("chunk", "")
                accumulated_text.append(chunk)
                yield PublicClientEvent(event="token_delta", data={"text": chunk})

            # 3. Tool execution progress: Sanitize internal tool arguments
            elif internal_evt.event_type == "on_tool_start":
                tool_name = internal_evt.payload.get("tool_name", "")
                if tool_name in cls.ALLOWED_PUBLIC_TOOLS:
                    yield PublicClientEvent(
                        event="tool_status",
                        data={"tool": tool_name, "status": "RUNNING"}
                    )

            elif internal_evt.event_type == "on_tool_end":
                tool_name = internal_evt.payload.get("tool_name", "")
                if tool_name in cls.ALLOWED_PUBLIC_TOOLS:
                    yield PublicClientEvent(
                        event="tool_status",
                        data={"tool": tool_name, "status": "COMPLETED"}
                    )

            # 4. Chain End: Validate structured output before emitting final completion!
            elif internal_evt.event_type == "on_chain_end":
                full_text = "".join(accumulated_text)
                valid, parsed_or_err = cls._validate_output_contract(full_text)
                if valid:
                    yield PublicClientEvent(event="final_answer", data={"result": parsed_or_err})
                else:
                    yield PublicClientEvent(event="error", data={"message": "Output contract validation failed", "details": parsed_or_err})

    @classmethod
    def _validate_output_contract(cls, text: str) -> Tuple[bool, Any]:
        """Validates that final output satisfies expected JSON schema."""
        try:
            parsed = json.loads(text)
            if not isinstance(parsed, dict) or "answer" not in parsed:
                return False, "Missing required 'answer' key in JSON payload"
            return True, parsed
        except json.JSONDecodeError as err:
            return False, f"Invalid JSON syntax: {err}"


def main():
    # Simulate internal framework stream containing private system prompts and token chunks
    internal_events = [
        InternalFrameworkEvent(
            event_type="on_chat_model_start",
            payload={"system_prompt": "SECRET INSTRUCTIONS: Act as corporate agent. API_KEY=sk-live-9941"},
            internal_metadata={"temperature": 0.2, "langchain_version": "0.3.0"}
        ),
        InternalFrameworkEvent(
            event_type="on_tool_start",
            payload={"tool_name": "search_kb", "query": "vacation policy", "db_connection_str": "postgres://admin:pass@db"},
            internal_metadata={"thread_id": "thr_001"}
        ),
        InternalFrameworkEvent(
            event_type="on_tool_end",
            payload={"tool_name": "search_kb", "raw_records": ["P1", "P2"]},
            internal_metadata={}
        ),
        InternalFrameworkEvent(
            event_type="on_chat_model_stream",
            payload={"chunk": '{"answer": "You '},
            internal_metadata={}
        ),
        InternalFrameworkEvent(
            event_type="on_chat_model_stream",
            payload={"chunk": 'have 15 days of PTO '},
            internal_metadata={}
        ),
        InternalFrameworkEvent(
            event_type="on_chat_model_stream",
            payload={"chunk": 'remaining."}'},
            internal_metadata={}
        ),
        InternalFrameworkEvent(
            event_type="on_chain_end",
            payload={},
            internal_metadata={}
        ),
    ]

    print("Transforming Internal Framework Events into Public Client Contract:")
    public_events = list(FrontendStreamAdapter.transform_event_stream(internal_events))

    for idx, pub_evt in enumerate(public_events, 1):
        print(f"SSE Frame {idx}:\n{pub_evt.to_sse_frame().strip()}")

    # Assertions
    # 1. Assert private system prompt and API key were completely stripped
    all_client_data = json.dumps([e.data for e in public_events])
    assert "SECRET INSTRUCTIONS" not in all_client_data
    assert "sk-live-9941" not in all_client_data
    assert "postgres://admin:pass@db" not in all_client_data
    assert "langchain_version" not in all_client_data

    # 2. Assert public client received standard event types
    event_names = [e.event for e in public_events]
    assert "tool_status" in event_names
    assert "token_delta" in event_names
    assert "final_answer" in event_names

    # 3. Assert final validated payload is clean JSON
    final_evt = public_events[-1]
    assert final_evt.event == "final_answer"
    assert final_evt.data["result"]["answer"] == "You have 15 days of PTO remaining."

    print("\nStream event adapter, client contract decoupling, and output validation verified successfully.")


if __name__ == "__main__":
    main()
