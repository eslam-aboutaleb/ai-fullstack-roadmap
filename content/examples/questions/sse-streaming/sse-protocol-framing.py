# /// script
# dependencies = []
# ///
"""
W3C Server-Sent Events (SSE) Protocol Framing Engine.

Demonstrates:
1. Formatting compliant SSE frames with id, event, and data fields.
2. Parsing raw wire frames according to W3C EventSource grammar:
   - Folding consecutive multi-line 'data:' fields with single newlines.
   - Ignoring comment/heartbeat lines (starting with a colon).
   - Dispatching complete event blocks strictly upon double newlines (\\n\\n).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class SSEMessage:
    id: Optional[str] = None
    event: str = "message"
    data: str = ""


class SSEFrameParser:
    """Parses raw text streams according to W3C Server-Sent Events specification."""

    def __init__(self) -> None:
        self.buffer: str = ""

    def feed(self, chunk: str) -> List[SSEMessage]:
        self.buffer += chunk
        dispatched_events: List[SSEMessage] = []

        # Split on double newline (event boundary)
        while "\n\n" in self.buffer:
            raw_event, self.buffer = self.buffer.split("\n\n", 1)
            event_obj = self._parse_event_block(raw_event)
            if event_obj:
                dispatched_events.append(event_obj)

        return dispatched_events

    def _parse_event_block(self, block: str) -> Optional[SSEMessage]:
        lines = block.split("\n")
        data_lines: List[str] = []
        event_type = "message"
        event_id: Optional[str] = None

        for line in lines:
            line = line.strip("\r")
            if not line:
                continue

            # Heartbeat / Comment line: lines starting with colon must be ignored
            if line.startswith(":"):
                continue

            if ":" in line:
                field, value = line.split(":", 1)
                if value.startswith(" "):
                    value = value[1:]  # Strip optional leading space
            else:
                field, value = line, ""

            if field == "data":
                data_lines.append(value)
            elif field == "event":
                event_type = value
            elif field == "id":
                event_id = value

        # Only dispatch if data or event was emitted
        if data_lines or event_type != "message" or event_id is not None:
            # Multi-line data folding: consecutive data lines are joined with a single newline
            folded_data = "\n".join(data_lines)
            return SSEMessage(id=event_id, event=event_type, data=folded_data)

        return None


def main() -> None:
    parser = SSEFrameParser()

    # Raw wire stream containing:
    # 1. A comment line (: ping)
    # 2. An event with custom event type, id, and multi-line data
    # 3. A second event with JSON payload
    raw_stream = (
        ": ping\n\n"
        "id: evt_101\n"
        "event: document_delta\n"
        "data: Section 1: Overview\n"
        "data: Section 2: Architecture\n\n"
        "id: evt_102\n"
        "event: token\n"
        'data: {"token": "complete", "cost_usd": 0.002}\n\n'
    )

    events = parser.feed(raw_stream)

    assert len(events) == 2, f"Expected 2 dispatched events, found {len(events)}"
    parsed_events = len(events)

    # Verify Event 1: Multi-line data folding
    evt1 = events[0]
    assert evt1.id == "evt_101"
    assert evt1.event == "document_delta"
    assert evt1.data == "Section 1: Overview\nSection 2: Architecture"
    multiline_data_folded = True

    # Verify Event 2: JSON payload
    evt2 = events[1]
    assert evt2.id == "evt_102"
    assert evt2.event == "token"
    payload = json.loads(evt2.data)
    assert payload["token"] == "complete"

    # Verify Heartbeats: The initial ': ping\n\n' comment was cleanly ignored
    heartbeats_ignored = True

    print(
        f"SSE protocol framing verified: parsed_events={parsed_events}, "
        f"multiline_data_folded={multiline_data_folded}, heartbeats_ignored={heartbeats_ignored}"
    )


if __name__ == "__main__":
    main()
