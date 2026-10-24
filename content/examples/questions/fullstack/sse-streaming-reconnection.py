"""Demonstrate Server-Sent Events (SSE) streaming with Last-Event-ID reconnection reconciliation."""

class SSEStreamServer:
    def __init__(self, full_tokens):
        # Buffered stream of events with monotonically increasing event IDs
        self.events = [
            {"id": i, "delta": tok} for i, tok in enumerate(full_tokens, 1)
        ]

    def format_sse_chunk(self, event):
        """Format chunk according to W3C EventSource standard."""
        return f"id: {event['id']}\nevent: token\ndata: {{\"delta\": \"{event['delta']}\"}}\n\n"

    def stream_from(self, last_event_id=0):
        """
        Reconnection handler:
        If client drops connection and reconnects with Last-Event-ID header,
        the server replays all events with id > last_event_id.
        """
        replayed = []
        for ev in self.events:
            if ev["id"] > last_event_id:
                replayed.append(self.format_sse_chunk(ev))
        return replayed

# Stream scenario: 6 tokens
tokens = ["The", " database", " transaction", " completed", " with", " success."]
server = SSEStreamServer(tokens)

# 1. Initial Connection: Client connects and receives tokens 1, 2, 3
initial_stream = server.stream_from(last_event_id=0)
received_tokens = []
for chunk in initial_stream[:3]:
    # Extract id and token
    ev_id = int(chunk.split("id: ")[1].split("\n")[0])
    token = chunk.split('"delta": "')[1].split('"')[0]
    received_tokens.append((ev_id, token))

assert len(received_tokens) == 3
last_seen_id = received_tokens[-1][0] # id = 3

# 2. SIMULATE NETWORK DROP: Wi-Fi reconnects, browser EventSource sends 'Last-Event-ID: 3'
reconnected_stream = server.stream_from(last_event_id=last_seen_id)

# 3. Server replays tokens 4, 5, 6:
for chunk in reconnected_stream:
    ev_id = int(chunk.split("id: ")[1].split("\n")[0])
    token = chunk.split('"delta": "')[1].split('"')[0]
    received_tokens.append((ev_id, token))

# Verify complete sentence reconstructed without duplicate or missing tokens:
full_text = "".join(t[1] for t in received_tokens)
assert full_text == "The database transaction completed with success."
assert [t[0] for t in received_tokens] == [1, 2, 3, 4, 5, 6]

print(f"SSE reconnection reconciliation verified: full_text='{full_text}', total_events={len(received_tokens)}")

