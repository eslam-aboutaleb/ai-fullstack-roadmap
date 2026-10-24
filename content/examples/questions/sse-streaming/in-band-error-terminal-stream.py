# /// script
# dependencies = []
# ///
"""
In-Band Error Transmission for Mid-Flight SSE Stream Failures.

Demonstrates:
1. The committed HTTP status code problem: once HTTP 200 OK headers are sent,
   a mid-stream failure cannot change the status code to HTTP 500.
2. Emitting an explicit in-band 'event: error' frame with a structured JSON payload
   (error code, safe user message, and retryable flag).
3. Graceful socket closure preventing infinite client reconnection loops.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional


class StreamingConnection:
    """Models a committed HTTP streaming connection."""

    def __init__(self) -> None:
        self.headers_committed: bool = False
        self.http_status: int = 0
        self.wire_messages: List[str] = []
        self.is_closed: bool = False

    def send_initial_headers(self) -> None:
        self.http_status = 200
        self.headers_committed = True

    def emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        if self.is_closed:
            raise RuntimeError("Cannot write to closed stream")
        frame = f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
        self.wire_messages.append(frame)

    def close(self) -> None:
        self.is_closed = True


class StreamingAgentHandler:
    def execute_stream(self, connection: StreamingConnection, fail_midway: bool) -> None:
        # Step 1: Commit initial 200 OK headers to initiate stream
        connection.send_initial_headers()

        # Step 2: Stream initial tokens
        connection.emit_event("delta", {"token": "Initiating "})
        connection.emit_event("delta", {"token": "vector search..."})

        # Step 3: Upstream failure occurs midway
        if fail_midway:
            # Cannot change HTTP status to 500! Must emit in-band error event:
            error_payload = {
                "code": "UPSTREAM_PROVIDER_TIMEOUT",
                "message": "Foundation model inference timed out after 30 seconds",
                "retryable": True,
            }
            connection.emit_event("error", error_payload)
            connection.close()
            return

        # Normal completion path
        connection.emit_event("complete", {"status": "SUCCESS"})
        connection.close()


def main() -> None:
    conn = StreamingConnection()
    handler = StreamingAgentHandler()

    # Execute stream with simulated midway failure
    handler.execute_stream(conn, fail_midway=True)

    # Invariant 1: HTTP Status code was committed as 200 OK before the failure
    assert conn.headers_committed is True
    assert conn.http_status == 200
    http_status_committed = conn.http_status

    # Invariant 2: Last event emitted before socket close was in-band 'event: error'
    last_frame = conn.wire_messages[-1]
    assert "event: error" in last_frame
    terminal_event_received = "error"

    # Invariant 3: Error payload is structured JSON with safe code and retryable flag
    data_line = [line for line in last_frame.splitlines() if line.startswith("data: ")][0]
    payload = json.loads(data_line[6:])
    assert payload["code"] == "UPSTREAM_PROVIDER_TIMEOUT"
    assert payload["retryable"] is True

    # Invariant 4: Clean socket termination
    assert conn.is_closed is True
    clean_termination = conn.is_closed

    print(
        f"In-band stream error verified: http_status_committed={http_status_committed}, "
        f"terminal_event_received={terminal_event_received}, clean_termination={clean_termination}"
    )


if __name__ == "__main__":
    main()
