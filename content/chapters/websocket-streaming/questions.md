<!-- chapter: websocket-streaming -->

# When should WebSockets replace SSE?

<!-- meta
domain: frontend
subdomain: websocket
module: websocket-streaming
concept: When should WebSockets replace SSE
difficulty: implementation
misconception_target: WebSocket connections are secure by default
added: true
review.status: draft
review.reviewer: independent technical review pending
review.reviewed_at: 2026-10-20
-->

## Answer

Use WebSockets when the client and server need low-latency bidirectional messaging during an active session, such as audio frames or collaborative control. SSE remains sufficient for many one-way progress streams.

## Spoken Summary

Use WebSocket when bidirectional application messaging justifies it. Choose an authentication approach compatible with the client, authorize every resource/action, bound unauthenticated work and revalidate expiring sessions. Define envelopes, sequence/replay, flow control and close/error behavior explicitly.

## Why

Compare required message direction, infrastructure, binary data needs, reconnect behavior, and authentication.

## Production Case

A browser reconnects with an expired session while old queued commands remain. Re-authenticate, scope replay and reconcile command identities rather than executing the queue under stale authority.

## Risk

Choosing WebSockets does not automatically improve application latency.

## Trade-off

Duplex sessions add lifecycle and routing complexity.

## Try This

Specify the messages that genuinely require a persistent bidirectional channel.

## Execution Timeline

Client connects -> Send auth token as first frame -> Server validates -> Exchange envelopes -> Apply flow control -> Close cleanly

## Complexity

Message handling scales with payload bytes, validation and dispatched work. Concurrent connections, buffered messages and replay retention determine memory; bidirectional transport does not create automatic flow control.

## Definitions

- **WebSocket envelope**: Message wrapper with type, sequence, and payload
- **Flow control**: Regulating message rate between producer and consumer
- **Envelope authentication**: Authentication at an explicitly chosen handshake or message boundary before any protected work, with per-action authorization.

## Alternatives

- SSE for server-to-client only
- HTTP long-polling

## Pitfalls

- No authentication
- No message envelopes
- No flow control

## Follow-ups

### Must WebSocket authentication always happen in the first frame?

No. Handshake-based session patterns and explicit message protocols have different constraints. If authenticating in a message, expose no protected work beforehand and bound timeout/message size.

## Example

> Explanation: Send auth on open, parse envelopes on message.
> Output: Authenticated bidirectional stream

```python
ws.onopen = () => ws.send(JSON.stringify({type: "auth", token}));\nws.onmessage = e => { const env = JSON.parse(e.data); handle(env); };
```

## Citations

- https://developer.mozilla.org/en-US/docs/Web/API/WebSocket

# How should WebSocket authentication work?

## Answer

Authenticate the handshake and authorize the session's resources, then recheck permissions for sensitive messages and long-lived sessions. Validate allowed origins for browser clients.

## Why

Use an explicit token or cookie strategy supported by the client and server. Handle expiry and revocation without logging credentials.

## Risk

A valid connection at startup can outlive the user's permission.

## Trade-off

Frequent revalidation adds work and limits stale access.

## Try This

Revoke a user's access during an active session and verify the next protected action is denied.

# What belongs in a WebSocket message envelope?

## Answer

Include schema version, session ID, message ID, sequence, type, correlation ID, and typed payload. Distinguish commands, acknowledgments, events, errors, and terminal states.

## Why

Validate message size and schema before dispatch. Use binary frames for audio where appropriate and explicit metadata for format.

## Risk

An untyped message bus invites accidental interpretation and oversized payload abuse.

## Trade-off

Verbose envelopes add bandwidth and improve evolution and diagnosis.

## Try This

Design a cancel command correlated with the generation it targets.

# How do acknowledgments and delivery guarantees work?

## Answer

TCP provides ordered bytes while connected; application acknowledgments establish which logical messages were processed. Reconnection needs explicit replay and deduplication rules.

## Why

Persist critical commands or outcomes with stable IDs and make repeated handling idempotent.

## Risk

Receiving a frame is not proof that a business transaction committed.

## Trade-off

Stronger delivery semantics add storage and protocol complexity.

## Try This

Disconnect between processing a command and sending its acknowledgment.

# How should flow control work for WebSockets?

## Answer

Bound inbound and outbound queues, limit frame sizes, and define how producers pause or shed nonessential progress. Standard browser WebSocket APIs do not provide automatic application backpressure.

## Why

Monitor buffered bytes and processing latency. Prioritize control messages such as cancellation over bulk content.

## Risk

An audio producer can overwhelm a slow consumer and cause memory growth or large delays.

## Trade-off

Dropping stale audio reduces latency and may affect intelligibility.

## Try This

Simulate a slow network and ensure cancellation still reaches the server promptly.

# What are ping, pong, and application heartbeats for?

## Answer

Transport-level ping and pong help detect connection liveness where exposed. Application heartbeats can verify end-to-end processing and carry session status.

## Why

Set timeouts compatible with proxies and mobile networks, and distinguish temporary silence from failure.

## Risk

A healthy connection does not prove that the agent or downstream service is progressing.

## Trade-off

Aggressive timeouts reduce dead sessions and create false disconnects.

## Try This

Pause the application worker while leaving the socket open and inspect health signals.

# How should reconnecting clients recover state?

## Answer

Reauthenticate, present a resume token or last processed sequence, and receive replay or a state snapshot. The server decides whether the old session can safely resume.

## Why

Expire resume capabilities, bind them to the owner, and deduplicate commands and events.

## Risk

Replaying every outbound client message can repeat a side effect.

## Trade-off

Durable recovery costs state storage and supports unstable networks.

## Try This

Reconnect after an ambiguous write and recover through its operation ID.

# How do WebSocket servers scale horizontally?

## Answer

Maintain durable session and task state outside one process, route active connections deliberately, and distribute events through a shared channel when needed.

## Why

Capacity-plan open connections, memory, bandwidth, worker count, and draining behavior. Sticky routing does not replace durable recovery.

## Risk

A process-local registry loses sessions on restart and cannot coordinate a fleet.

## Trade-off

Shared infrastructure adds latency and enables scale and recovery.

## Try This

Drain one instance during active sessions and verify the expected reconnect path.

# How should binary audio and text events coexist?

## Answer

Define a protocol that identifies audio format, stream, timestamps, and sequence while using typed control events for transcripts and state. Keep ordering assumptions explicit.

## Why

Validate sample rate, channels, codec, and payload size. Maintain separate playback and control queues when useful.

## Risk

Misinterpreted encoding can produce noise, broken timing, or excessive memory use.

## Trade-off

A richer protocol adds implementation work and supports multimodal sessions.

## Try This

Change the declared audio format midstream and verify a controlled rejection.

# What should a WebSocket production test include?

## Answer

Test authorization, origin checks, oversized frames, expired sessions, malformed messages, reconnects, duplicate commands, slow consumers, network loss, and deployment draining.

## Why

Measure end-to-end command latency and queue depth under realistic concurrency.

## Risk

A local echo server does not establish reliability of a distributed agent session.

## Trade-off

Load tests require representative infrastructure and reveal connection capacity limits.

## Try This

Publish a capacity report with connection count, memory use, and p95 control-message latency.

# How do WebSockets and Server-Sent Events compare in bidirectional streaming, binary frame transport, and protocol overhead?

<!-- meta
answer_format: conceptual
domain: frontend
subdomain: websocket-streaming
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**WebSockets and Server-Sent Events (SSE) represent two distinct real-time web protocols engineered for contrasting communication topologies.** WebSockets (RFC 6455) provide a full-duplex, bidirectional communication channel over a single TCP connection, established via an initial HTTP Upgrade handshake. Server-Sent Events (WHATWG) provide a unidirectional, server-to-client streaming channel over standard HTTP/1.1 chunked transfer encoding or HTTP/2 streams.\n\n**Architectural comparison across protocol dimensions:**\n(1) Communication Directionality: WebSockets allow both client and server to transmit messages independently at any time.

SSE is strictly unidirectional: only the server can push events; client-to-server communications require sending separate standard HTTP POST/PUT requests.\n(2) Binary vs Text Transport: WebSockets support raw binary frames (ArrayBuffer, Blob) with minimal 2–10 byte framing overhead, making them ideal for audio PCM streaming, video frames, and high-frequency sensor telemetry. SSE is strictly UTF-8 text-based (`data: ...\n\n`); streaming binary data requires Base64 encoding, which adds a 33% bandwidth overhead.\n(3) Corporate Firewalls and HTTP/2 Multiplexing: SSE runs over standard HTTP, traversing corporate proxies, VPNs, and API gateways effortlessly while supporting HTTP/2 multiplexing (multiple SSE streams over a single TCP connection). WebSockets require custom reverse proxy configuration (`Upgrade: websocket`) and frequently fail behind corporate inspection firewalls.

## Why

An AI voice agent requires streaming 24kHz raw PCM audio bidirectionally. WebSockets handle raw binary frames with 2-byte framing overhead. In contrast, an AI chat completion only pushes text tokens from server to client; SSE is vastly superior due to built-in HTTP reconnection and proxy compatibility.

## Worked Case

An AI voice agent requires streaming 24kHz raw PCM audio bidirectionally. WebSockets handle raw binary frames with 2-byte framing overhead. In contrast, an AI chat completion only pushes text tokens from server to client; SSE is vastly superior due to built-in HTTP reconnection and proxy compatibility.

## Risk

Using WebSockets for simple unidirectional text streaming adds complex connection lifecycle management, custom heartbeat loops, and authentication renegotiation without any protocol benefit.

## Trade-off

WebSockets support high-performance binary full-duplex messaging at the cost of operational complexity; SSE provides simple, robust text push over standard HTTP infrastructure.

## Try This

Benchmark the wire bandwidth overhead of sending 1,000 binary audio packets over WebSockets vs Base64-encoded SSE. Measure the 33% payload expansion in SSE.

## Follow-ups

### Can SSE pass authorization headers during EventSource connection?

Standard browser EventSource does not support custom headers; modern applications use the fetch() API with ReadableStream to pass Bearer tokens while reading SSE format.

## Citations

- https://www.rfc-editor.org/rfc/rfc6455
- https://html.spec.whatwg.org/multipage/server-sent-events.html

# How do WebSocket heartbeat pings and exponential backoff reconnection maintain connection vitality through proxy timeouts?

<!-- meta
answer_format: conceptual
domain: frontend
subdomain: websocket-streaming
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Intermediate cloud proxies, load balancers, and NAT gateways silently drop idle TCP connections after 60–120 seconds unless kept alive by heartbeat frames.** In WebSocket applications, when an agent or user is not actively chatting, no application data flows over the socket. Cloud load balancers (such as AWS ALB, Cloudflare, or Nginx) enforce aggressive idle timeouts: if zero packets traverse the TCP connection within 60 seconds, the proxy silently drops the connection by removing the NAT table entry without sending a TCP FIN or RST packet to either party.\n\n**Silent half-open connections.** Both client and server believe the connection is still alive (a 'half-open' socket). When the server eventually attempts to push a token, the packet is blackholed, throwing connection errors.\n\n**Heartbeat ping/pong protocol.** The WebSocket specification provides native control frames: Ping (opcode `0x9`) and Pong (opcode `0xA`).

The server or client periodically transmits a Ping every 30 seconds; the receiver immediately responds with an identical Pong frame. If the sender fails to receive a Pong within 5 seconds, it concludes the connection is dead, immediately closes the socket, and triggers reconnection.\n\n**Jittered exponential backoff reconnection.** When reconnecting, clients must never reconnect immediately in a tight loop, which creates a 'thundering herd' that crushes backend servers during recovery. Clients use exponential backoff with full jitter: `delay = random(0, min(max_delay, base_delay * 2^attempt))`. Adding randomness decorrelates thousands of client reconnections.

## Why

An AWS ALB has a 60s idle timeout. A user pauses typing for 65 seconds. Without a 30s heartbeat ping, the ALB silently severs the connection, causing the next message send to fail with a broken pipe error.

## Worked Case

An AWS ALB has a 60s idle timeout. A user pauses typing for 65 seconds. Without a 30s heartbeat ping, the ALB silently severs the connection, causing the next message send to fail with a broken pipe error.

## Risk

Reconnecting without randomized jitter causes thousands of dropped mobile clients to reconnect at the exact identical millisecond, overwhelming API gateways.

## Trade-off

Heartbeat frames consume tiny network bandwidth (a few bytes every 30 seconds), but guarantee instant detection of silent connection drops.

## Try This

Set up a WebSocket connection through Nginx with `proxy_read_timeout 10s`. Send messages every 15s without heartbeats and observe the 504 timeout; enable a 5s ping/pong loop and observe continuous connectivity.

## Follow-ups

### Can browser JavaScript send native WebSocket ping frames?

No. The browser's WebSocket API handles protocol-level ping/pongs automatically under the hood; applications that need custom application-level heartbeats send text frames like `{"type": "ping"}`.

## Citations

- https://www.rfc-editor.org/rfc/rfc6455#section-5.5.2
- https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/

# How do you prevent message re-ordering and data loss during WebSocket reconnection using sequence numbering and client-side ring buffers?

<!-- meta
answer_format: conceptual
domain: frontend
subdomain: websocket-streaming
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Transient network disconnections during WebSocket streaming cause in-flight message drops and out-of-order deliveries unless governed by sequence numbering and unacknowledged message buffers.** When an agent streams structured output or financial updates over a WebSocket, a momentary cellular handoff or Wi-Fi glitch drops the TCP socket while the server is in the middle of transmitting messages #45 through #50.\n\n**The double failure: data loss and out-of-order arrival.** If the client reconnects and requests a fresh state, messages #45–#50 are permanently lost. Furthermore, if client-to-server messages were queued in flight during disconnection, re-sending them without sequence tracking can result in out-of-order execution (e.g., executing a 'Transfer' command after a 'Cancel' command).\n\n**The Sequence Numbering and Ring Buffer protocol:**\n(1) Monotonic Sequence Numbers: Every message emitted by the server or client is stamped with an integer `seq_num` (1, 2, 3...);\n(2) Server-Side Unacknowledged Ring Buffer: The server stores the last N transmitted messages in an in-memory ring buffer (e.g.

last 1,000 messages or 60 seconds of history);\n(3) Client Acknowledgment (ACK): The client periodically sends `{"type": "ack", "last_seq": 44}`. The server prunes messages <= 44 from its ring buffer;\n(4) Reconnection Resumption: When the client reconnects, its initial handshake payload includes `last_seen_seq: 44`. The server immediately replays messages 45 through 50 from its ring buffer before streaming live events; and\n(5) Client Deduplication: If the client receives a message with `seq_num <= current_local_seq`, it silently discards it, guaranteeing exactly-once processing.

## Why

A user's network drops during an AI response at word 40. The client reconnects with `last_seen_seq: 40`. The server replays words 41–50 and continues generation seamlessly, with zero duplicated or missing sentences.

## Worked Case

A user's network drops during an AI response at word 40. The client reconnects with last_seen_seq: 40. The server replays words 41–50 and continues generation seamlessly, with zero duplicated or missing sentences.

## Risk

Failing to bound the server-side ring buffer with a maximum TTL or memory cap causes memory exhaustion if clients disconnect permanently without sending ACKs.

## Trade-off

Sequence buffering requires maintaining session buffers on server instances, trading small memory overhead for robust network resilience and zero data loss.

## Try This

Simulate dropping a WebSocket client after message 5. Reconnect passing `last_seq: 5` and verify that the server replays messages 6 through 10 before resuming live traffic.

## Follow-ups

### What happens if a client is disconnected for longer than the ring buffer retention limit?

The server returns an `ERR_SESSION_EXPIRED` code, instructing the client to purge its local state and execute a complete state rehydration from the database.

## Citations

- https://www.rfc-editor.org/rfc/rfc6455
- https://en.wikipedia.org/wiki/Sliding_window_protocol

# How do you horizontally scale WebSocket connections across multiple server replicas using Redis Pub/Sub backplanes?

<!-- meta
answer_format: conceptual
domain: frontend
subdomain: websocket-streaming
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Horizontally scaling stateful WebSocket connections requires an asynchronous publish-subscribe message backplane to route messages across distributed server pods.** In standard stateless HTTP APIs, any application replica behind a load balancer can handle any request. In WebSockets, connections are persistent and stateful: Client A is connected via TCP to Server Pod 1, while Client B is connected to Server Pod 2.

If Client B sends a chat message destined for Client A, Server Pod 2 cannot write directly to Client A's socket because it resides on a different physical machine.\n\n**The Redis Pub/Sub backplane architecture.** To connect isolated server replicas, production architectures deploy an in-memory distributed message broker (such as Redis Pub/Sub, Redis Streams, or RabbitMQ) as a cross-replica backplane:\n(1) Subscription: When Client A connects to Pod 1 and joins room `chat_room_42`, Pod 1 subscribes to the Redis channel `room:chat_room_42`;\n(2) Publication: When Client B on Pod 2 posts a message to `chat_room_42`, Pod 2 publishes the message payload to Redis: `PUBLISH room:chat_room_42 "{...}"`;\n(3) Distribution: Redis broadcasts the message to all server pods subscribed to that channel (Pod 1); and\n(4) Local Delivery: Pod 1 receives the Redis event and pushes the message down the local TCP socket to Client A.\n\n**Connection limits and Epoll optimization.** A single Linux server process can easily maintain 50,000–100,000 idle WebSocket connections using non-blocking I/O event loops (`epoll` via libuv in Node or uvloop in Python). Production configurations must tune Linux kernel file descriptor limits (`ulimit -n 65536`) and TCP buffer sizes to prevent socket starvation.

## Why

A multi-user document collaboration session has 10 users distributed across 4 Kubernetes pods. Redis Pub/Sub broadcasts user edits across all 4 pods in sub-5ms, keeping all 10 users in sync regardless of which pod holds their TCP socket.

## Worked Case

A multi-user document collaboration session has 10 users distributed across 4 Kubernetes pods. Redis Pub/Sub broadcasts user edits across all 4 pods in sub-5ms, keeping all 10 users in sync regardless of which pod holds their TCP socket.

## Risk

Standard Redis Pub/Sub is fire-and-forget: if a pod's Redis subscriber disconnects momentarily during a network glitch, messages broadcast during that window are permanently lost.

## Trade-off

Redis Pub/Sub provides sub-millisecond cross-pod broadcasting with minimal latency, at the cost of running and monitoring an external shared Redis cluster.

## Try This

Spin up two independent WebSocket server instances on different ports connected to a local Redis container. Connect one client to port 8001 and another to port 8002, and verify that messages broadcast across them via Redis.

## Follow-ups

### How do Redis Streams differ from Redis Pub/Sub for WebSocket backplanes?

Redis Streams provide durable, persistent message logging and consumer groups with acknowledgments, allowing dropped pods to recover missed messages upon reconnection.

## Citations

- https://redis.io/docs/latest/develop/interact/pubsub/
- https://socket.io/docs/v4/redis-adapter/

# How do you keep a reconnected WebSocket from accepting stale or unauthorized commands?

<!-- meta
domain: frontend
subdomain: websocket-streaming
module: websocket-streaming
concept: How do you keep a reconnected WebSocket from accepting stale or unauthorized commands?
difficulty: scenario
misconception_target: Assuming this concrete failure is excluded by a happy-path success: A delayed command from a previous session overwrites a newer operation after reconnect because the server checks only socket establishment.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Authenticate the connection or declared application handshake, then authorize each consequential command against current scope and state. Use operation identities, sequence or revision rules and bounded replay. A new socket does not necessarily mean a new logical task, and an old socket should not retain indefinite authority after a session change.

Concrete engineering case: A delayed command from a previous session overwrites a newer operation after reconnect because the server checks only socket establishment.

Boundary defense: No. The transport and browser constraints determine a supported handshake pattern. Whatever the mechanism, verify current authority where effects occur.

## Spoken Summary

Authenticate the connection or declared application handshake, then authorize each consequential command against current scope and state. Use operation identities, sequence or revision rules and bounded replay. A new socket does not necessarily mean a new logical task, and an old socket should not retain indefinite authority after a session change.

## Why

Authenticate the connection or declared application handshake, then authorize each consequential command against current scope and state. Use operation identities, sequence or revision rules and bounded replay. A new socket does not necessarily mean a new logical task, and an old socket should not retain indefinite authority after a session change.

## Production Case

A delayed command from a previous session overwrites a newer operation after reconnect because the server checks only socket establishment.

## Risk

A delayed command from a previous session overwrites a newer operation after reconnect because the server checks only socket establishment.

## Trade-off

No. The transport and browser constraints determine a supported handshake pattern. Whatever the mechanism, verify current authority where effects occur.

## Try This

Reproduce this case with synthetic data, state the authoritative result and show a regression that rejects the broken behavior.

## Execution Timeline

Identify the authoritative state → trace the failure boundary → inspect durable or visible evidence → test the proposed recovery

## Complexity

Include workload size, retained state, latency, concurrency and recovery work under the declared assumptions; the reasoning fixture is not a capacity benchmark.

## Definitions

- **Boundary: websocket streaming**: Authenticate the connection or declared application handshake, then authorize each consequential command against current scope and state.

## Alternatives

- No. The transport and browser constraints determine a supported handshake pattern. Whatever the mechanism, verify current authority where effects occur.

## Pitfalls

- A delayed command from a previous session overwrites a newer operation after reconnect because the server checks only socket establishment.

## Follow-ups

### Must authentication always be the first WebSocket message?

No. The transport and browser constraints determine a supported handshake pattern. Whatever the mechanism, verify current authority where effects occur.

## Example

> Explanation: A source-linked reasoning fixture. JSON parsing checks representation only; reproduce the actual mechanism with the chapter reference.
> Output: No runtime or production measurement is inferred from this reasoning fixture.

```python
{
  "scenario": "A delayed command from a previous session overwrites a newer operation after reconnect because the server checks only socket establishment.",
  "required_decision": "Authenticate the connection or declared application handshake, then authorize each consequential command against current scope and state"
}
```

## Citations

- https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API

# How do WebSocket flow control, heartbeats and reconnect state prevent silent corruption?

<!-- meta
answer_format: conceptual
domain: frontend
subdomain: websocket-streaming
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A bidirectional connection needs application message identities, ordering expectations and bounded send/receive queues. Heartbeats help detect an unresponsive peer but do not prove that an earlier message's effect failed. On reconnect, authenticate again and resume through a documented cursor or authoritative status lookup. Do not replay arbitrary commands as fresh operations. The browser WebSocket interface and a server's library may offer different backpressure mechanisms, so enforce application limits rather than assuming an unlimited transport buffer is safe.

## Why

An audio client reconnects while old frames remain queued. Frames from the previous session must not be attached to the new turn; use session and turn identities and discard or reconcile obsolete queued data.

## Worked Case

An audio client reconnects while old frames remain queued. Frames from the previous session must not be attached to the new turn; use session and turn identities and discard or reconcile obsolete queued data.

## Risk

A healthy open socket can still accumulate an unbounded application backlog.

## Trade-off

Flow control preserves bounded resources at the cost of dropping, rejecting or slowing work explicitly.

## Try This

Simulate a slow consumer, a lost heartbeat and a reconnect with stale queued messages.

## Citations

- https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API
