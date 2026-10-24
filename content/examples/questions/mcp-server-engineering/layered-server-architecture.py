"""Layered production MCP server architecture and protocol adapter isolation.

Demonstrates:
1. Four-tier architectural layering:
   - Transport Adapter (stdio / HTTP streamable framing)
   - Protocol Dispatcher (JSON-RPC 2.0 routing)
   - Schema Validation & Argument Coercion
   - Core Domain Service (authoritative business logic, permissions, repository queries)
2. Decoupled business logic: Domain service reused across both MCP tool adapters and REST endpoints without logic duplication.
3. Minimal Python MCP tool registration and execution.
"""
from typing import Any, Dict, List, Optional, Tuple
import json

# --- TIER 4: AUTHORITATIVE DOMAIN SERVICE (PURE BUSINESS LOGIC) ---
class DocumentDomainService:
    """Core domain service owning business logic, database queries, and authorization rules."""
    def __init__(self):
        self._database = {
            "doc-101": {"title": "Production Deployment Guide", "body": "Follow blue-green deployment checklist.", "tenant": "corp-alpha"},
            "doc-102": {"title": "Database Runbook", "body": "Execute vacuum analyze during maintenance windows.", "tenant": "corp-alpha"}
        }

    def fetch_document_excerpt(self, caller_tenant: str, doc_id: str, max_chars: int) -> Dict[str, Any]:
        # Domain invariant 1: Resource must exist
        if doc_id not in self._database:
            raise KeyError(f"Document '{doc_id}' does not exist.")

        record = self._database[doc_id]

        # Domain invariant 2: Multi-tenant ownership check
        if record["tenant"] != caller_tenant:
            raise PermissionError(f"Access denied: Document '{doc_id}' does not belong to tenant '{caller_tenant}'.")

        # Domain invariant 3: Bounded business excerpt calculation
        excerpt = record["body"][:max_chars]
        return {
            "doc_id": doc_id,
            "title": record["title"],
            "excerpt": excerpt,
            "truncated": len(record["body"]) > max_chars
        }

# --- TIER 3 & 2: MCP PROTOCOL ADAPTER & DISPATCHER ---
class McpToolAdapter:
    """Thin protocol adapter translating JSON-RPC requests to domain service calls."""
    def __init__(self, domain_service: DocumentDomainService):
        self.domain_service = domain_service

    def get_tool_descriptor(self) -> Dict[str, Any]:
        return {
            "name": "get_document_excerpt",
            "description": "Retrieves an authorized document excerpt by ID with bounded length.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "doc_id": {"type": "string"},
                    "max_chars": {"type": "integer", "minimum": 10, "maximum": 500}
                },
                "required": ["doc_id"]
            }
        }

    def dispatch_tool_call(self, caller_tenant: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        # Tier 3: Validation & parameter coercion
        doc_id = arguments.get("doc_id")
        if not doc_id or not isinstance(doc_id, str):
            return {
                "content": [{"type": "text", "text": "Validation Error: 'doc_id' string is required."}],
                "isError": True
            }

        max_chars = arguments.get("max_chars", 100)
        if not isinstance(max_chars, int) or max_chars < 10 or max_chars > 500:
            return {
                "content": [{"type": "text", "text": "Validation Error: 'max_chars' must be between 10 and 500."}],
                "isError": True
            }

        # Tier 4: Delegate to authoritative domain service
        try:
            result = self.domain_service.fetch_document_excerpt(caller_tenant, doc_id, max_chars)
            return {
                "content": [{"type": "text", "text": json.dumps(result)}],
                "isError": False
            }
        except KeyError as ke:
            return {
                "content": [{"type": "text", "text": f"Not Found: {str(ke)}"}],
                "isError": True
            }
        except PermissionError as pe:
            return {
                "content": [{"type": "text", "text": f"Permission Denied: {str(pe)}"}],
                "isError": True
            }

# --- SIMULATED HTTP CONTROLLER (REUSING SAME DOMAIN SERVICE) ---
class HttpRestController:
    """Demonstrates that non-MCP HTTP routes reuse the exact same domain service."""
    def __init__(self, domain_service: DocumentDomainService):
        self.domain_service = domain_service

    def get_document_endpoint(self, caller_tenant: str, doc_id: str, max_chars: int = 100) -> Tuple[int, Dict[str, Any]]:
        try:
            data = self.domain_service.fetch_document_excerpt(caller_tenant, doc_id, max_chars)
            return 200, data
        except KeyError as e:
            return 404, {"error": str(e)}
        except PermissionError as e:
            return 403, {"error": str(e)}

if __name__ == "__main__":
    service = DocumentDomainService()
    mcp_adapter = McpToolAdapter(service)
    http_controller = HttpRestController(service)

    # 1. MCP Tool Execution (Happy path)
    mcp_ok = mcp_adapter.dispatch_tool_call(caller_tenant="corp-alpha", arguments={"doc_id": "doc-101", "max_chars": 50})
    assert mcp_ok["isError"] is False
    assert "blue-green" in mcp_ok["content"][0]["text"]

    # 2. Reused Domain Logic: HTTP endpoint executes identical business rules
    http_status, http_data = http_controller.get_document_endpoint(caller_tenant="corp-alpha", doc_id="doc-101", max_chars=50)
    assert http_status == 200
    assert "blue-green" in http_data["excerpt"]

    # 3. Cross-Tenant Protection enforced identically in MCP and HTTP
    mcp_denied = mcp_adapter.dispatch_tool_call(caller_tenant="corp-beta", arguments={"doc_id": "doc-101"})
    assert mcp_denied["isError"] is True
    assert "Permission Denied" in mcp_denied["content"][0]["text"]

    http_status, http_err = http_controller.get_document_endpoint(caller_tenant="corp-beta", doc_id="doc-101")
    assert http_status == 403
    assert "Access denied" in http_err["error"]

    # 4. Tool input validation failure
    mcp_bad_args = mcp_adapter.dispatch_tool_call(caller_tenant="corp-alpha", arguments={"doc_id": "doc-101", "max_chars": 5000})
    assert mcp_bad_args["isError"] is True
    assert "between 10 and 500" in mcp_bad_args["content"][0]["text"]

    print("Layered MCP server architecture and domain service isolation verified successfully.")

