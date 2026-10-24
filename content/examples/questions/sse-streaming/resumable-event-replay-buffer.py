# /// script
# dependencies = []
# ///
"""
Resumable SSE Event Stream with Last-Event-ID Cursor Recovery.

Demonstrates:
1. Server-side event ring buffer assigning monotonic event IDs.
2. Client disconnection mid-stream and reconnect with Last-Event-ID header.
3. Server resuming transmission from the requested offset without restart.
4. Client-side deduplication filter preventing duplicate text tokens.
"""

from __future__ import annotations

from typing import Dict, List, Optional


class SSEReplayBuffer:
    """Server-side ring buffer preserving recent streaming events for reconnection."""

    def __init__(self, capacity: int = 50) -> None:
        self.capacity = capacity
        self.events: List[Dict[str, Any]] = []

    def append_event(self, event_id: int, token: str) -> None:
        self.events.append({"id": event_id, "token": token})
        if len(self.events) > self.capacity:
            self.events.pop(0)

    def replay_from(self, last_event_id: Optional[int]) -> List[Dict[str, Any]]:
        if last_event_id is None:
            return list(self.events)
        return [evt for evt in self.events if evt["id"] > last_event_id]


class ClientStreamReceiver:
    """Client-side stream receiver with cursor tracking and token deduplication."""

    def __init__(self) -> None:
        self.highest_received_id: int = 0
        self.assembled_text: str = ""
        self.duplicate_tokens_encountered: int = 0

    def receive_event(self, event: Dict[str, Any]) -> None:
        event_id = event["id"]
        # Client deduplication filter
        if event_id <= self.highest_received_id:
            self.duplicate_tokens_encountered += 1
            return  # Drop duplicate re-transmission

        self.highest_received_id = event_id
        self.assembled_text += event["token"]


def main() -> None:
    server_buffer = SSEReplayBuffer(capacity=20)
    client = ClientStreamReceiver()

    # Server generates 7 token events
    full_message = ["Thinking", " ", "in", " ", "autonomous", " ", "systems"]
    for idx, word in enumerate(full_message, start=1):
        server_buffer.append_event(event_id=idx, token=word)

    # 1. Client connects initially and receives events 1 to 4
    initial_stream = server_buffer.replay_from(last_event_id=None)[:4]
    for evt in initial_stream:
        client.receive_event(evt)

    assert client.highest_received_id == 4
    assert client.assembled_text == "Thinking in "
    reconnected_from_id = client.highest_received_id

    # 2. Network drop occurs! Client reconnects sending Last-Event-ID: 4
    replayed_stream = server_buffer.replay_from(last_event_id=client.highest_received_id)
    assert len(replayed_stream) == 3, f"Expected 3 replayed events, found {len(replayed_stream)}"
    replayed_events = len(replayed_stream)

    # 3. Simulate accidental re-transmission of event 4 alongside 5..7
    accidental_packet_burst = [server_buffer.events[3]] + replayed_stream
    for evt in accidental_packet_burst:
        client.receive_event(evt)

    # Invariant: Duplicate token was dropped cleanly
    assert client.duplicate_tokens_encountered == 1, "Duplicate token was not caught by deduplication filter"
    duplicate_tokens = 0  # Zero duplicate tokens in final assembled text

    # Final assembled text is completely clean and matches full sequence
    assert client.assembled_text == "Thinking in autonomous systems"

    print(
        f"Resumable SSE replay verified: reconnected_from_id={reconnected_from_id}, "
        f"replayed_events={replayed_events}, duplicate_tokens={duplicate_tokens}"
    )


if __name__ == "__main__":
    main()
