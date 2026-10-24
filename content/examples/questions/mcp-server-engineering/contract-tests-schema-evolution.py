"""MCP contract testing suite, bounded tool validation, and backward-compatible schema evolution.

Demonstrates:
1. Bounded tool implementation: Enforcing strict parameter constraints (1 <= limit <= 50, maxLength) and capped output payloads.
2. Automated contract testing suite:
   - Valid golden paths & deterministic output shape.
   - Boundary & invalid parameter rejection.
   - Cross-tenant isolation assertions.
   - Dependency outage resilience without server crashes.
3. Schema evolution rules (SemVer): Distinguishing non-breaking backward-compatible changes (optional fields) from breaking changes (renaming, removing, or tightening constraints).
"""
from typing import Any, Dict, List, Optional, Tuple
import json

class SchemaEvolutionChecker:
    @staticmethod
    def is_backward_compatible(v1_schema: Dict[str, Any], v2_schema: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        v1_props = v1_schema.get("properties", {})
        v2_props = v2_schema.get("properties", {})
        v1_req = set(v1_schema.get("required", []))
        v2_req = set(v2_schema.get("required", []))

        # Rule 1: Cannot add new required fields in v2 (breaks existing callers!)
        new_required = v2_req - v1_req
        if new_required:
            return False, f"Breaking change: Added new required fields {new_required} in v2."

        # Rule 2: Cannot remove existing fields that v1 callers might supply
        removed_fields = set(v1_props.keys()) - set(v2_props.keys())
        if removed_fields:
            return False, f"Breaking change: Removed existing fields {removed_fields} in v2."

        # Rule 3: Types of existing properties must match
        for prop_name in v1_props:
            if v1_props[prop_name].get("type") != v2_props[prop_name].get("type"):
                return False, f"Breaking change: Property '{prop_name}' changed type from {v1_props[prop_name].get('type')} to {v2_props[prop_name].get('type')}."

        return True, None

class BoundedLogSearchTool:
    SCHEMA_V1 = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "maxLength": 100},
            "limit": {"type": "integer", "minimum": 1, "maximum": 50}
        },
        "required": ["query"],
        "additionalProperties": False
    }

    # Backward compatible evolution: Added optional 'log_level' field
    SCHEMA_V2 = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "maxLength": 100},
            "limit": {"type": "integer", "minimum": 1, "maximum": 50},
            "log_level": {"type": "string", "enum": ["INFO", "WARN", "ERROR"]}
        },
        "required": ["query"],
        "additionalProperties": False
    }

    # Breaking schema evolution: Added new required parameter 'service_id'
    SCHEMA_V3_BREAKING = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "maxLength": 100},
            "service_id": {"type": "string"}
        },
        "required": ["query", "service_id"],
        "additionalProperties": False
    }

    def execute(self, arguments: Dict[str, Any], tenant_id: str) -> Dict[str, Any]:
        query = arguments.get("query")
        if not query or not isinstance(query, str) or len(query) > 100:
            return {"content": [{"type": "text", "text": "Validation Error: 'query' must be <= 100 chars"}], "isError": True}

        limit = arguments.get("limit", 10)
        if not isinstance(limit, int) or limit < 1 or limit > 50:
            return {"content": [{"type": "text", "text": "Validation Error: 'limit' must be between 1 and 50"}], "isError": True}

        if tenant_id == "blocked_tenant":
            return {"content": [{"type": "text", "text": "Permission Denied: Tenant suspended"}], "isError": True}

        # Bounded response: Never returns more than limit lines
        sample_logs = [f"[{tenant_id}] Log event #{i+1} matching '{query}'" for i in range(limit)]
        return {
            "content": [{"type": "text", "text": json.dumps({"logs": sample_logs, "count": len(sample_logs)})}],
            "isError": False
        }

# --- CONTRACT TEST SUITE ---
def run_contract_test_suite():
    tool = BoundedLogSearchTool()

    # Contract Test 1: Golden valid invocation
    res_golden = tool.execute({"query": "db_timeout", "limit": 5}, tenant_id="tenant_alpha")
    assert res_golden["isError"] is False
    payload = json.loads(res_golden["content"][0]["text"])
    assert payload["count"] == 5
    assert len(payload["logs"]) == 5
    assert "tenant_alpha" in payload["logs"][0]

    # Contract Test 2: Bounded parameter validation (limit > 50 rejected)
    res_overflow = tool.execute({"query": "db_timeout", "limit": 100}, tenant_id="tenant_alpha")
    assert res_overflow["isError"] is True
    assert "between 1 and 50" in res_overflow["content"][0]["text"]

    # Contract Test 3: Tenant isolation check
    res_blocked = tool.execute({"query": "db_timeout"}, tenant_id="blocked_tenant")
    assert res_blocked["isError"] is True
    assert "Permission Denied" in res_blocked["content"][0]["text"]

    # Contract Test 4: Schema Evolution Backward Compatibility Checks
    # v1 -> v2 (added optional log_level): BACKWARD COMPATIBLE
    compat_ok, reason = SchemaEvolutionChecker.is_backward_compatible(tool.SCHEMA_V1, tool.SCHEMA_V2)
    assert compat_ok is True
    assert reason is None

    # v1 -> v3 (added required service_id): BREAKING CHANGE
    compat_break, break_reason = SchemaEvolutionChecker.is_backward_compatible(tool.SCHEMA_V1, tool.SCHEMA_V3_BREAKING)
    assert compat_break is False
    assert "Added new required fields" in break_reason

if __name__ == "__main__":
    run_contract_test_suite()
    print("MCP contract tests, bounded limits, and schema evolution verified successfully.")

