# Stream progress without confusing it with completion
Typed public events connect the backend, browser, and audio session while durable state remains authoritative.

@answer scope="Illustrative SSE, WebSocket, and voice design"
@meta locale=en

## Adapt events for the client
@sequence id=delivery-flow title="Persistence before completion"
| actor client | Browser or voice client | frontend |
| actor api | API and session gateway | backend |
| actor agent | Agent runtime | backend |
| actor store | Task and result store | database |
| client | api | Start task or send audio |
| api | agent | Trusted identity and task ID |
| agent | api | Safe text or tool progress | return |
| api | client | Typed ordered events | return |
| agent | store | Persist final result |
| store | agent | Durable result ID | return |
| agent | api | Completed with result ID | return |
| api | client | Terminal event | return |

## Choose the transport
| Need | Candidate | Extra responsibility |
| --- | --- | --- |
| One-way text or progress | SSE | Replay, parsing, disconnects |
| Duplex control and binary frames | WebSocket | Flow control and session recovery |
| Interactive media | WebRTC where supported | Signaling and scoped credentials |
| Any transport | Durable task service | Status and cancellation |
