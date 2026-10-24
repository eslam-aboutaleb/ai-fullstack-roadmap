# /// script
# dependencies = []
# ///
"""
Horizontal Scaling of Stateful WebSockets via Distributed Pub/Sub Backplane.

Demonstrates:
1. Multi-replica architecture: Client A connects to Pod 1, Client B to Pod 2.
2. Background agent worker on Pod 3 publishes events to a shared message bus (Redis).
3. Pods 1 and 2 consume the event and broadcast to their respective local clients.
4. Solves the horizontal WebSocket scaling challenge without sticky routing limits.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class MockWebSocketClient:
    client_id: str
    received_messages: List[str] = field(default_factory=list)

    def send(self, message: str) -> None:
        self.received_messages.append(message)


class DistributedMessageBus:
    """Simulated Redis Pub/Sub backplane."""

    def __init__(self) -> None:
        self.subscribers: Dict[str, List[Any]] = {}

    def subscribe(self, channel: str, callback: Any) -> None:
        self.subscribers.setdefault(channel, []).append(callback)

    def publish(self, channel: str, message: str) -> None:
        for callback in self.subscribers.get(channel, []):
            callback(message)


class WebSocketServerPod:
    """Server replica holding a local subset of active client connections."""

    def __init__(self, pod_name: str, bus: DistributedMessageBus) -> None:
        self.pod_name = pod_name
        self.bus = bus
        self.local_clients: Dict[str, MockWebSocketClient] = {}

    def attach_client(self, client: MockWebSocketClient, topic: str) -> None:
        self.local_clients[client.client_id] = client
        # Subscribe to pub/sub channel
        self.bus.subscribe(topic, lambda msg: self._broadcast_to_topic(topic, msg))

    def _broadcast_to_topic(self, topic: str, message: str) -> None:
        for client in self.local_clients.values():
            client.send(message)


def main() -> None:
    bus = DistributedMessageBus()

    # Replicas deployed across cluster
    pod_alpha = WebSocketServerPod(pod_name="pod_alpha", bus=bus)
    pod_bravo = WebSocketServerPod(pod_name="pod_bravo", bus=bus)

    # Client A connects to Pod Alpha, Client B connects to Pod Bravo
    client_a = MockWebSocketClient(client_id="client_a")
    client_b = MockWebSocketClient(client_id="client_b")

    task_channel = "tasks.tsk_7721.events"
    pod_alpha.attach_client(client_a, topic=task_channel)
    pod_bravo.attach_client(client_b, topic=task_channel)

    # Background agent worker on an independent worker node emits completion event
    worker_message = '{"event": "task_completed", "task_id": "tsk_7721", "tokens": 420}'
    bus.publish(task_channel, worker_message)

    # Invariant: Both clients on different pods receive the message via backplane
    assert len(client_a.received_messages) == 1
    assert "task_completed" in client_a.received_messages[0]
    client_alpha_received = True

    assert len(client_b.received_messages) == 1
    assert "task_completed" in client_b.received_messages[0]
    client_bravo_received = True

    cross_replica_delivered = client_alpha_received and client_bravo_received

    print(
        f"Distributed WebSocket scale verified: cross_replica_delivered={cross_replica_delivered}, "
        f"client_alpha_received={client_alpha_received}, client_bravo_received={client_bravo_received}"
    )


if __name__ == "__main__":
    main()
