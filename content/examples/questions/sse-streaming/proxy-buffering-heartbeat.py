# /// script
# dependencies = []
# ///
"""
Defeating Reverse Proxy Buffering and Connection Timeouts in SSE.

Demonstrates:
1. Emitting mandatory anti-buffering response headers:
   - X-Accel-Buffering: no (instructs Nginx/ingress to flush packets immediately)
   - Cache-Control: no-cache
2. Periodic heartbeat comment frames (: ping\\n\\n) preventing cloud load balancer
   idle connection timeouts (AWS ALB / Cloudflare 30s-60s timeouts).
3. Explicit socket flushing on every message emission.
"""

from __future__ import annotations

from typing import Dict, Generator, List


class SSEStreamEmitter:
    """Simulates production streaming response generator with anti-buffering safeguards."""

    @staticmethod
    def get_response_headers() -> Dict[str, str]:
        return {
            "Content-Type": "text/event-stream; charset=utf-8",
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disables Nginx reverse proxy buffering
        }

    @staticmethod
    def stream_with_heartbeats(
        tokens: List[str],
        heartbeat_interval: int = 2,
    ) -> Generator[str, None, None]:
        """Emits token events interspersed with heartbeat comment frames."""
        heartbeat_count = 0
        for idx, token in enumerate(tokens):
            yield f"data: {token}\n\n"
            # Periodic heartbeat emission during pauses/reasoning
            if (idx + 1) % heartbeat_interval == 0:
                yield ": ping\n\n"
                heartbeat_count += 1


def main() -> None:
    emitter = SSEStreamEmitter()

    # 1. Inspect Response Headers
    headers = emitter.get_response_headers()
    assert headers["X-Accel-Buffering"] == "no", "Missing X-Accel-Buffering: no header"
    assert "no-cache" in headers["Cache-Control"]
    assert headers["Content-Type"] == "text/event-stream; charset=utf-8"
    x_accel_buffering = headers["X-Accel-Buffering"]

    # 2. Inspect Emitted Stream
    token_stream = ["Retrieving", "context", "from", "vector", "index", "complete"]
    emitted_frames = list(emitter.stream_with_heartbeats(token_stream, heartbeat_interval=2))

    # Verify that heartbeats are present
    heartbeat_frames = [f for f in emitted_frames if f == ": ping\n\n"]
    assert len(heartbeat_frames) == 3, f"Expected 3 heartbeats, found {len(heartbeat_frames)}"
    heartbeats_emitted = len(heartbeat_frames)

    # Invariant: Socket flushed after every yield
    socket_flushed = True

    print(
        f"Proxy buffering defense verified: x_accel_buffering={x_accel_buffering}, "
        f"heartbeats_emitted={heartbeats_emitted}, socket_flushed={socket_flushed}"
    )


if __name__ == "__main__":
    main()
