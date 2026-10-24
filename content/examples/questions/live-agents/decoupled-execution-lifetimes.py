"""Decoupled Execution Lifetimes: Connection vs Session vs Task.

Demonstrates that transport connection, conversational session, and durable task
execution boundaries are strictly decoupled. When an ephemeral socket drops, the
conversational session preserves state and background tasks run to completion.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ConnectionState(str, Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class EphemeralConnection:
    connection_id: str
    user_id: str
    state: ConnectionState = ConnectionState.CONNECTED
    active_session_id: Optional[str] = None


@dataclass
class ConversationalSession:
    session_id: str
    user_id: str
    memory_history: List[str] = field(default_factory=list)
    attached_task_ids: List[str] = field(default_factory=list)
    is_active: bool = True


@dataclass
class DurableTask:
    task_id: str
    session_id: str
    prompt: str
    status: TaskStatus = TaskStatus.PENDING
    progress_percent: int = 0
    result: Optional[str] = None


class LiveAgentGateway:
    """Orchestrates connection transports, session memory, and durable worker tasks."""

    def __init__(self) -> None:
        self.connections: Dict[str, EphemeralConnection] = {}
        self.sessions: Dict[str, ConversationalSession] = {}
        self.tasks: Dict[str, DurableTask] = {}

    def open_connection(self, connection_id: str, user_id: str) -> EphemeralConnection:
        conn = EphemeralConnection(connection_id=connection_id, user_id=user_id)
        self.connections[connection_id] = conn
        return conn

    def bind_session(self, connection_id: str, session_id: str) -> ConversationalSession:
        conn = self.connections[connection_id]
        if session_id not in self.sessions:
            self.sessions[session_id] = ConversationalSession(
                session_id=session_id, user_id=conn.user_id
            )
        conn.active_session_id = session_id
        return self.sessions[session_id]

    def dispatch_durable_task(self, session_id: str, task_id: str, prompt: str) -> DurableTask:
        session = self.sessions[session_id]
        task = DurableTask(task_id=task_id, session_id=session_id, prompt=prompt, status=TaskStatus.RUNNING)
        self.tasks[task_id] = task
        session.attached_task_ids.append(task_id)
        session.memory_history.append(f"Dispatched task {task_id}: {prompt}")
        return task

    def disconnect_transport(self, connection_id: str) -> None:
        """Simulate an abrupt mobile network blip or socket termination."""
        if connection_id in self.connections:
            self.connections[connection_id].state = ConnectionState.DISCONNECTED

    def progress_background_worker(self, task_id: str, final_result: str) -> None:
        """Simulate autonomous worker progressing independently of transport presence."""
        task = self.tasks[task_id]
        task.progress_percent = 100
        task.status = TaskStatus.COMPLETED
        task.result = final_result

    def reconnect_and_fetch_task(
        self, new_conn_id: str, session_id: str, task_id: str
    ) -> Dict[str, Any]:
        """Client reconnects over new transport, re-attaches to session, and polls task."""
        conn = self.open_connection(new_conn_id, user_id=self.sessions[session_id].user_id)
        self.bind_session(new_conn_id, session_id)
        task = self.tasks[task_id]
        return {
            "new_connection_state": conn.state.value,
            "session_active": self.sessions[session_id].is_active,
            "task_status": task.status.value,
            "result": task.result,
        }


def test_decoupled_lifetimes() -> None:
    gateway = LiveAgentGateway()

    # Step 1: User connects via WebSocket (Connection 1) and opens Session S100
    c1 = gateway.open_connection("conn_ws_01", user_id="usr_alice")
    session = gateway.bind_session("conn_ws_01", "sess_alice_conv")
    assert c1.state == ConnectionState.CONNECTED
    assert session.session_id == "sess_alice_conv"

    # Step 2: User requests a long-running research synthesis
    task = gateway.dispatch_durable_task(
        session_id="sess_alice_conv",
        task_id="tsk_market_analysis_42",
        prompt="Synthesize competitive landscape across 50 SEC filings",
    )
    assert task.status == TaskStatus.RUNNING
    assert "tsk_market_analysis_42" in session.attached_task_ids

    # Step 3: Wi-Fi drops! Transport connection terminates abruptly
    gateway.disconnect_transport("conn_ws_01")
    assert gateway.connections["conn_ws_01"].state == ConnectionState.DISCONNECTED

    # Invariant: Neither session nor background task is cancelled by connection loss
    assert gateway.sessions["sess_alice_conv"].is_active is True
    assert gateway.tasks["tsk_market_analysis_42"].status == TaskStatus.RUNNING

    # Step 4: Worker completes durable job while user is disconnected
    gateway.progress_background_worker(
        task_id="tsk_market_analysis_42",
        final_result="Market synthesis complete: 3 emerging threats identified.",
    )
    assert gateway.tasks["tsk_market_analysis_42"].status == TaskStatus.COMPLETED

    # Step 5: User reconnects over cellular network (Connection 2)
    reconnect_receipt = gateway.reconnect_and_fetch_task(
        new_conn_id="conn_cellular_02",
        session_id="sess_alice_conv",
        task_id="tsk_market_analysis_42",
    )

    assert reconnect_receipt["new_connection_state"] == "connected"
    assert reconnect_receipt["task_status"] == "completed"
    assert "3 emerging threats" in reconnect_receipt["result"]
    assert gateway.connections["conn_ws_01"].state == ConnectionState.DISCONNECTED
    assert gateway.connections["conn_cellular_02"].state == ConnectionState.CONNECTED

    print(
        f"Decoupled execution lifetimes verified: original_connection=disconnected, "
        f"task_status={reconnect_receipt['task_status']}, "
        f"reconnected_result_delivered=True"
    )


if __name__ == "__main__":
    test_decoupled_lifetimes()
