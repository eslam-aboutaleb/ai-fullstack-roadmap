# /// script
# dependencies = []
# ///
"""
Per-Command Authorization and Dynamic Revocation on Long-Lived WebSockets.

Demonstrates:
1. Re-checking token expiration on incoming command frames.
2. Rejecting commands when initial handshake token expires without refresh.
3. Administrative revocation broadcasts instantly terminating active sessions.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple


@dataclass
class WebSocketSession:
    session_id: str
    user_id: str
    token_expires_at: float
    is_revoked: bool = False
    is_socket_open: bool = True


class WebSocketSecurityGateway:
    def __init__(self) -> None:
        self.sessions: Dict[str, WebSocketSession] = {}

    def create_session(
        self,
        session_id: str,
        user_id: str,
        ttl_seconds: float,
        start_time: Optional[float] = None,
    ) -> WebSocketSession:
        base_time = start_time if start_time is not None else time.time()
        session = WebSocketSession(
            session_id=session_id,
            user_id=user_id,
            token_expires_at=base_time + ttl_seconds,
        )
        self.sessions[session_id] = session
        return session

    def execute_command(
        self,
        session_id: str,
        action: str,
        current_time: Optional[float] = None,
    ) -> Tuple[int, Dict[str, Any]]:
        now = current_time if current_time is not None else time.time()
        session = self.sessions.get(session_id)

        if not session:
            return 404, {"error": "SESSION_NOT_FOUND"}

        # 1. Check administrative revocation
        if session.is_revoked:
            session.is_socket_open = False
            return 403, {"error": "SESSION_REVOKED", "message": "Permissions revoked by administrator"}

        if not session.is_socket_open:
            return 404, {"error": "SOCKET_CLOSED"}

        # 2. Check token expiration (cannot rely solely on handshake timestamp!)
        if now > session.token_expires_at:
            session.is_socket_open = False
            return 401, {"error": "TOKEN_EXPIRED", "message": "Handshake token expired; refresh required"}

        return 200, {"status": "SUCCESS", "action": action}

    def revoke_user_sessions(self, user_id: str) -> None:
        """Administrative event (e.g. from Redis pub/sub) invalidating user."""
        for session in self.sessions.values():
            if session.user_id == user_id:
                session.is_revoked = True
                session.is_socket_open = False


def main() -> None:
    gateway = WebSocketSecurityGateway()
    start_time = 1000.0

    # User establishes session with token expiring in 60s (at time 1060.0)
    session = gateway.create_session("sess_01", user_id="usr_alice", ttl_seconds=60.0, start_time=start_time)

    # 1. Command 1 arrives at t = 1010s (Token is valid)
    code_1, resp_1 = gateway.execute_command("sess_01", "get_status", current_time=1010.0)
    assert code_1 == 200
    assert resp_1["status"] == "SUCCESS"
    initial_command_authorized = True

    # 2. Command 2 arrives at t = 1070s (Token expired 10s ago!)
    code_2, resp_2 = gateway.execute_command("sess_01", "transfer_funds", current_time=1070.0)
    assert code_2 == 401
    assert resp_2["error"] == "TOKEN_EXPIRED"
    assert session.is_socket_open is False, "Socket should be severed on token expiration"
    expired_token_rejected = True

    # 3. Administrative Revocation mid-session
    session_2 = gateway.create_session("sess_02", user_id="usr_bob", ttl_seconds=3600.0)
    # Admin revokes Bob's account
    gateway.revoke_user_sessions("usr_bob")

    code_3, resp_3 = gateway.execute_command("sess_02", "query_crm", current_time=1010.0)
    assert code_3 == 403
    assert resp_3["error"] == "SESSION_REVOKED"
    assert session_2.is_socket_open is False
    revoked_session_closed = True

    print(
        f"WebSocket session auth verified: initial_command_authorized={initial_command_authorized}, "
        f"expired_token_rejected={expired_token_rejected}, "
        f"revoked_session_closed={revoked_session_closed}"
    )


if __name__ == "__main__":
    main()
