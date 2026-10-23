"""MCP tool error modeling, domain error taxonomy, and LLM self-correction contracts.

Demonstrates:
1. Domain error hierarchy: ValidationError, ResourceNotFoundError, PermissionDeniedError, DependencyRateLimitedError.
2. Mapping domain exceptions to MCP CallToolResult with isError: true.
3. Structuring actionable error payloads that enable agent self-correction without leaking stack traces or internal secrets.
4. Reserving JSON-RPC protocol error codes (-32xxx) strictly for transport/framing failures.
"""
from typing import Any, Dict, List, Optional
import json
import uuid

# --- DOMAIN EXCEPTION TAXONOMY ---
class McpDomainException(Exception):
    def __init__(self, code: str, message: str, actionable_guidance: str, status_code: int = 400):
        super().__init__(message)
        self.code = code
        self.message = message
        self.actionable_guidance = actionable_guidance
        self.status_code = status_code

class ValidationError(McpDomainException):
    def __init__(self, message: str, actionable_guidance: str):
        super().__init__("VALIDATION_ERROR", message, actionable_guidance, 422)

class ResourceNotFoundError(McpDomainException):
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            "RESOURCE_NOT_FOUND",
            f"{resource_type} '{resource_id}' was not found in the current workspace.",
            f"Verify the {resource_type.lower()} identifier or call search_{resource_type.lower()}s to discover valid IDs.",
            404
        )

class DependencyRateLimitedError(McpDomainException):
    def __init__(self, service_name: str, retry_after_seconds: int):
        super().__init__(
            "RATE_LIMITED",
            f"Upstream service '{service_name}' exceeded concurrency rate limits.",
            f"Wait {retry_after_seconds} seconds before retrying this tool call.",
            429
        )

# --- MCP ERROR TRANSLATOR ---
class McpErrorPresenter:
    @staticmethod
    def format_domain_error(exception: McpDomainException, correlation_id: Optional[str] = None) -> Dict[str, Any]:
        trace_id = correlation_id or f"trace_{uuid.uuid4().hex[:12]}"
        
        # Structured payload formatted specifically for LLM reasoning and agent loops
        error_payload = {
            "error_category": exception.code,
            "message": exception.message,
            "guidance": exception.actionable_guidance,
            "correlation_id": trace_id
        }

        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(error_payload, indent=2)
                }
            ],
            "isError": True
        }

    @staticmethod
    def format_unexpected_crash(exception: Exception, correlation_id: Optional[str] = None) -> Dict[str, Any]:
        trace_id = correlation_id or f"trace_{uuid.uuid4().hex[:12]}"
        # NEVER leak stack traces, database credentials, or server paths to the model!
        safe_payload = {
            "error_category": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected server fault occurred while executing the capability.",
            "guidance": "Do not retry with the same arguments. Report the correlation ID to technical support.",
            "correlation_id": trace_id
        }
        return {
            "content": [{"type": "text", "text": json.dumps(safe_payload, indent=2)}],
            "isError": True
        }

# Simulated tool demonstrating error dispatch
def simulated_tool_dispatch(action: str, target_id: str) -> Dict[str, Any]:
    trace_id = "trace_mcp_audit_01"
    try:
        if action == "find_order":
            if target_id == "ord_unknown":
                raise ResourceNotFoundError("Order", target_id)
            elif not target_id.startswith("ord_"):
                raise ValidationError("Order ID must begin with 'ord_' prefix.", "Provide ID formatted as ord_<numeric_id>.")
            return {
                "content": [{"type": "text", "text": json.dumps({"order_id": target_id, "status": "SHIPPED"})}],
                "isError": False
            }
        elif action == "query_upstream":
            raise DependencyRateLimitedError("PaymentGateway", 15)
        elif action == "crash":
            raise ConnectionResetError("Database connection lost at /var/run/postgres.sock with credentials admin:secret")
        raise ValidationError(f"Unknown action: '{action}'", "Check tools/list for available action names.")

    except McpDomainException as de:
        return McpErrorPresenter.format_domain_error(de, correlation_id=trace_id)
    except Exception as unexpected:
        return McpErrorPresenter.format_unexpected_crash(unexpected, correlation_id=trace_id)

if __name__ == "__main__":
    # 1. Resource Not Found Error: Exposes actionable guidance for agent recovery
    res_not_found = simulated_tool_dispatch("find_order", "ord_unknown")
    assert res_not_found["isError"] is True
    data_nf = json.loads(res_not_found["content"][0]["text"])
    assert data_nf["error_category"] == "RESOURCE_NOT_FOUND"
    assert "search_orders" in data_nf["guidance"]
    assert data_nf["correlation_id"] == "trace_mcp_audit_01"

    # 2. Validation Error
    res_val = simulated_tool_dispatch("find_order", "bad_format_123")
    assert res_val["isError"] is True
    data_val = json.loads(res_val["content"][0]["text"])
    assert data_val["error_category"] == "VALIDATION_ERROR"
    assert "ord_" in data_val["guidance"]

    # 3. Rate Limited Error with backoff guidance
    res_rl = simulated_tool_dispatch("query_upstream", "ord_101")
    assert res_rl["isError"] is True
    data_rl = json.loads(res_rl["content"][0]["text"])
    assert data_rl["error_category"] == "RATE_LIMITED"
    assert "Wait 15 seconds" in data_rl["guidance"]

    # 4. Unexpected crash: Internal sensitive stack trace redacted!
    res_crash = simulated_tool_dispatch("crash", "ord_101")
    assert res_crash["isError"] is True
    data_crash = json.loads(res_crash["content"][0]["text"])
    assert data_crash["error_category"] == "INTERNAL_SERVER_ERROR"
    # Secrets and socket paths MUST NOT be in the user/model-facing text
    assert "admin:secret" not in res_crash["content"][0]["text"]
    assert "/var/run/postgres.sock" not in res_crash["content"][0]["text"]
    assert data_crash["correlation_id"] == "trace_mcp_audit_01"

    print("MCP tool error modeling and domain taxonomy verified successfully.")
