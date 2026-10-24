# /// script
# dependencies = []
# ///
"""
Incremental SSE Parser Boundary Handling Multibyte UTF-8 and Event Splitting.

Demonstrates:
1. Handling simultaneous UTF-8 byte fragmentation (multibyte character split across chunks).
2. Handling event boundary delimiter fragmentation (\\n\\n split across chunks).
3. Safely accumulating unparsed fragments in remainder buffer without corruption.
4. Dispatching intact parsed JSON event objects to client listeners.
"""

from __future__ import annotations

import codecs
import json
from typing import Any, Dict, List, Optional


class StreamingSSEParser:
    """Production streaming parser handling both UTF-8 byte and protocol delimiter splits."""

    def __init__(self) -> None:
        self.decoder = codecs.getincrementaldecoder("utf-8")()
        self.remainder_buffer: str = ""

    def feed_bytes(self, byte_chunk: bytes, is_last: bool = False) -> List[Dict[str, Any]]:
        # 1. Incremental UTF-8 byte decoding
        decoded_text = self.decoder.decode(byte_chunk, final=is_last)
        self.remainder_buffer += decoded_text

        dispatched_events: List[Dict[str, Any]] = []

        # 2. Extract complete frames delimited by \n\n
        while "\n\n" in self.remainder_buffer:
            raw_event, self.remainder_buffer = self.remainder_buffer.split("\n\n", 1)
            parsed = self._parse_event(raw_event)
            if parsed:
                dispatched_events.append(parsed)

        return dispatched_events

    def _parse_event(self, raw_block: str) -> Optional[Dict[str, Any]]:
        data_lines: List[str] = []
        event_type = "message"
        event_id = None

        for line in raw_block.split("\n"):
            line = line.strip("\r")
            if not line or line.startswith(":"):
                continue  # Ignore heartbeats

            if ":" in line:
                k, v = line.split(":", 1)
                v = v.lstrip(" ")
                if k == "data":
                    data_lines.append(v)
                elif k == "event":
                    event_type = v
                elif k == "id":
                    event_id = v

        if not data_lines:
            return None

        combined_data = "\n".join(data_lines)
        try:
            parsed_payload = json.loads(combined_data)
        except Exception:
            parsed_payload = combined_data

        return {"id": event_id, "event": event_type, "data": parsed_payload}


def main() -> None:
    parser = StreamingSSEParser()

    # Create an SSE event stream with an emoji 🚀 (0xF0 0x9F 0x9A 0x80)
    full_wire_text = (
        'id: 1\nevent: token\ndata: {"status": "launching 🚀"}\n\n'
        'id: 2\nevent: done\ndata: {"finished": true}\n\n'
    )
    wire_bytes = full_wire_text.encode("utf-8")

    # Deliberately construct two pathological network chunks:
    # Chunk 1 splits directly in the middle of the 4-byte emoji 🚀
    emoji_pos = wire_bytes.index("🚀".encode("utf-8"))
    split_pos_1 = emoji_pos + 2  # Cuts emoji in half!

    # Chunk 2 ends inside the \n\n delimiter of the first event (e.g. data: ...}\n)
    # with the second \n arriving in Chunk 3!
    delimiter_pos = full_wire_text.index("\n\n") + 1

    chunk_1 = wire_bytes[:split_pos_1]
    chunk_2 = wire_bytes[split_pos_1:delimiter_pos]
    chunk_3 = wire_bytes[delimiter_pos:]

    # Feed Chunk 1: Partial emoji is held in decoder buffer
    events_1 = parser.feed_bytes(chunk_1)
    assert len(events_1) == 0, "No event should be dispatched from incomplete multibyte chunk"

    # Feed Chunk 2: Emoji completes, but event ends with single \n; held in remainder buffer
    events_2 = parser.feed_bytes(chunk_2)
    assert len(events_2) == 0, "No event should be dispatched before double newline boundary"
    multibyte_split_resolved = True

    # Feed Chunk 3: Second \n arrives, completing event 1, followed by event 2
    events_3 = parser.feed_bytes(chunk_3, is_last=True)
    assert len(events_3) == 2, f"Expected 2 events dispatched, found {len(events_3)}"
    delimiter_split_resolved = True

    # Validate Event 1 data integrity
    assert events_3[0]["data"]["status"] == "launching 🚀"
    assert events_3[0]["id"] == "1"

    # Validate Event 2
    assert events_3[1]["data"]["finished"] is True
    assert events_3[1]["id"] == "2"
    events_dispatched = len(events_3)

    print(
        f"Incremental SSE parser boundary verified: multibyte_split_resolved={multibyte_split_resolved}, "
        f"delimiter_split_resolved={delimiter_split_resolved}, events_dispatched={events_dispatched}"
    )


if __name__ == "__main__":
    main()
