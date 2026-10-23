"""MCP initialization handshake and capability negotiation state machine.

Demonstrates:
1. Three-way initialization handshake: initialize request -> InitializeResult -> notifications/initialized.
2. Protocol version negotiation across wire profiles (e.g., '2024-11-05').
3. Bidirectional capability exchange (tools, resources with subscriptions, prompts, logging, roots, sampling).
4. Strict state machine enforcement: Disallowing operational requests before handshake completion.
"""
from typing import Any, Dict, List, Optional
import enum

class HandshakeState(enum.Enum):
    UNINITIALIZED = "UNINITIALIZED"
    INITIALIZING = "INITIALIZING"
    INITIALIZED = "INITIALIZED"
    CLOSED = "CLOSED"

class McpConnection:
    SUPPORTED_VERSIONS = ["2024-11-05", "2024-10-07"]

    def __init__(self, server_name: str, server_version: str):
        self.state = HandshakeState.UNINITIALIZED
        self.server_info = {"name": server_name, "version": server_version}
        self.negotiated_version: Optional[str] = None
        self.client_capabilities: Dict[str, Any] = {}
        self.server_capabilities = {
            "tools": {"listChanged": True},
            "resources": {"subscribe": True, "listChanged": True},
            "prompts": {"listChanged": True},
            "logging": {}
        }

    def receive_initialize(self, request_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        if self.state != HandshakeState.UNINITIALIZED:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32600, "message": "Server already initialized or initializing"}
            }

        client_version = params.get("protocolVersion")
        if client_version not in self.SUPPORTED_VERSIONS:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32602,
                    "message": f"Unsupported protocol version '{client_version}'. Supported: {self.SUPPORTED_VERSIONS}"
                }
            }

        self.negotiated_version = client_version
        self.client_capabilities = params.get("capabilities", {})
        self.state = HandshakeState.INITIALIZING

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": self.negotiated_version,
                "capabilities": self.server_capabilities,
                "serverInfo": self.server_info
            }
        }

    def receive_initialized_notification(self) -> None:
        if self.state != HandshakeState.INITIALIZING:
            raise RuntimeError(f"Unexpected initialized notification in state: {self.state}")
        self.state = HandshakeState.INITIALIZED

    def dispatch_request(self, request_id: Any, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        # Enforce that tools/resources cannot be executed before handshake confirmation
        if self.state != HandshakeState.INITIALIZED:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32600,
                    "message": "Invalid Request: Session must be fully initialized. Awaiting 'notifications/initialized'."
                }
            }

        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"tools": [{"name": "echo", "description": "Echo input"}]}
            }
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"}
        }

if __name__ == "__main__":
    conn = McpConnection("enterprise-mcp-gateway", "1.4.0")
    assert conn.state == HandshakeState.UNINITIALIZED

    # 1. Premature request before initialization is rejected
    premature_resp = conn.dispatch_request(1, "tools/list", {})
    assert premature_resp["error"]["code"] == -32600
    assert "Awaiting 'notifications/initialized'" in premature_resp["error"]["message"]

    # 2. Unsupported protocol version rejected
    bad_init = conn.receive_initialize(2, {
        "protocolVersion": "2023-01-01",
        "capabilities": {},
        "clientInfo": {"name": "legacy-agent", "version": "0.1"}
    })
    assert bad_init["error"]["code"] == -32602
    assert conn.state == HandshakeState.UNINITIALIZED

    # 3. Successful initialize handshake
    init_resp = conn.receive_initialize(3, {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "roots": {"listChanged": True},
            "sampling": {}
        },
        "clientInfo": {"name": "ide-assistant", "version": "2.0.0"}
    })
    assert init_resp["result"]["protocolVersion"] == "2024-11-05"
    assert init_resp["result"]["capabilities"]["tools"]["listChanged"] is True
    assert conn.state == HandshakeState.INITIALIZING

    # Still rejected because notification hasn't arrived
    still_premature = conn.dispatch_request(4, "tools/list", {})
    assert still_premature["error"]["code"] == -32600

    # 4. Client sends notifications/initialized
    conn.receive_initialized_notification()
    assert conn.state == HandshakeState.INITIALIZED

    # 5. Operational requests now succeed
    tools_resp = conn.dispatch_request(5, "tools/list", {})
    assert "result" in tools_resp
    assert tools_resp["result"]["tools"][0]["name"] == "echo"

    print("MCP initialization handshake and capability state machine verified successfully.")
