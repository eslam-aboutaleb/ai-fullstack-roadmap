"""Model Context Protocol (MCP) JSON-RPC 2.0 framing and dispatch pipeline.

Demonstrates:
1. Strict JSON-RPC 2.0 message parsing: Request (id, method, params), Response (id, result/error), Notification (no id).
2. Protocol-level error codes (-32700 Parse, -32600 Invalid Request, -32601 Method Not Found, -32602 Invalid Params, -32603 Internal).
3. The vital architectural distinction: Application tool execution errors return as valid results with isError: true, NOT JSON-RPC protocol error frames.
4. Architectural dispatch boundaries: MCP capability calls vs A2A long-running task delegations vs REST CRUD operations.
"""
from typing import Any, Dict, Optional, Tuple
import json

class JsonRpcError(Exception):
    def __init__(self, code: int, message: str, data: Optional[Any] = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.data = data

    def to_frame(self, request_id: Optional[Any] = None) -> Dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": self.code,
                "message": self.message,
                **({"data": self.data} if self.data is not None else {})
            }
        }

class McpDispatcher:
    def __init__(self):
        self._handlers = {}
        self._notifications = {}
        self._active_a2a_tasks = {}

    def register_method(self, method: str, handler):
        self._handlers[method] = handler

    def register_notification(self, method: str, handler):
        self._notifications[method] = handler

    def handle_raw_message(self, raw_bytes: str) -> Optional[Dict[str, Any]]:
        # 1. Parse JSON
        try:
            payload = json.loads(raw_bytes)
        except Exception as e:
            return JsonRpcError(-32700, f"Parse error: {str(e)}").to_frame(None)

        if not isinstance(payload, dict):
            return JsonRpcError(-32600, "Invalid Request: root must be a JSON object").to_frame(None)

        if payload.get("jsonrpc") != "2.0":
            return JsonRpcError(-32600, "Invalid Request: jsonrpc version must be exactly '2.0'").to_frame(payload.get("id"))

        method = payload.get("method")
        if not method or not isinstance(method, str):
            return JsonRpcError(-32600, "Invalid Request: method string is required").to_frame(payload.get("id"))

        req_id = payload.get("id")
        params = payload.get("params", {})
        if not isinstance(params, (dict, list)):
            return JsonRpcError(-32602, "Invalid params: params must be object or array").to_frame(req_id)

        # 2. Check if Notification (No ID present)
        if "id" not in payload:
            if method in self._notifications:
                self._notifications[method](params)
            return None  # Notifications MUST NOT receive any JSON-RPC response frame

        # 3. Request execution
        if method not in self._handlers:
            return JsonRpcError(-32601, f"Method not found: '{method}'").to_frame(req_id)

        try:
            result = self._handlers[method](params)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": result
            }
        except JsonRpcError as je:
            return je.to_frame(req_id)
        except Exception as ex:
            return JsonRpcError(-32603, f"Internal error: {str(ex)}").to_frame(req_id)

# Domain handlers demonstrating protocol vs application error handling
def tool_call_handler(params: Dict[str, Any]) -> Dict[str, Any]:
    name = params.get("name")
    args = params.get("arguments", {})
    
    if name == "get_stock_quote":
        ticker = args.get("ticker", "").upper()
        if ticker == "FAIL":
            # Application-level failure: Return isError: true inside result!
            return {
                "content": [
                    {"type": "text", "text": "Ticker 'FAIL' not found on exchange. Verify ticker symbol."}
                ],
                "isError": True
            }
        return {
            "content": [
                {"type": "text", "text": json.dumps({"ticker": ticker, "price": 142.50, "currency": "USD"})}
            ],
            "isError": False
        }
    raise JsonRpcError(-32602, f"Unknown tool: '{name}'")

def a2a_delegate_task(params: Dict[str, Any]) -> Dict[str, Any]:
    """A2A task delegation: Unlike immediate MCP tools, creates a tracked durable task with lifecycle."""
    task_id = f"task_{params.get('agent')}_001"
    return {
        "task_id": task_id,
        "status": "SUBMITTED",
        "task_type": "A2A_DELEGATION",
        "poll_interval_seconds": 2
    }

if __name__ == "__main__":
    dispatcher = McpDispatcher()
    dispatcher.register_method("tools/call", tool_call_handler)
    dispatcher.register_method("tasks/delegate", a2a_delegate_task)
    dispatcher.register_notification("notifications/initialized", lambda p: print("Handshake confirmed!"))

    # Test 1: Valid tool call request
    res1 = dispatcher.handle_raw_message(json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": "get_stock_quote", "arguments": {"ticker": "AAPL"}}
    }))
    assert res1["id"] == 1
    assert res1["result"]["isError"] is False
    assert "142.5" in res1["result"]["content"][0]["text"]

    # Test 2: Tool execution failure (isError: True inside JSON-RPC result, NOT a protocol error!)
    res2 = dispatcher.handle_raw_message(json.dumps({
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {"name": "get_stock_quote", "arguments": {"ticker": "FAIL"}}
    }))
    assert res2["id"] == 2
    assert "error" not in res2  # No JSON-RPC error frame!
    assert res2["result"]["isError"] is True
    assert "not found" in res2["result"]["content"][0]["text"]

    # Test 3: Protocol error - Method not found (-32601)
    res3 = dispatcher.handle_raw_message(json.dumps({
        "jsonrpc": "2.0",
        "id": 3,
        "method": "unknown/method",
        "params": {}
    }))
    assert res3["id"] == 3
    assert res3["error"]["code"] == -32601

    # Test 4: Notification - No response frame emitted
    res4 = dispatcher.handle_raw_message(json.dumps({
        "jsonrpc": "2.0",
        "method": "notifications/initialized",
        "params": {}
    }))
    assert res4 is None

    # Test 5: A2A delegation returns durable task identity
    res5 = dispatcher.handle_raw_message(json.dumps({
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tasks/delegate",
        "params": {"agent": "researcher", "goal": "Index RFC 6570"}
    }))
    assert res5["result"]["task_type"] == "A2A_DELEGATION"
    assert res5["result"]["status"] == "SUBMITTED"

    print("MCP JSON-RPC 2.0 framing and dispatch verified successfully.")
