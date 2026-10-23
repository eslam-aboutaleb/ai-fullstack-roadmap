"""Demonstrate typed storage error semantics: distinguishing retriable timeouts from terminal errors."""

class StorageResult:
    def __init__(self, status, data=None, error_code=None, is_retriable=False):
        self.status = status
        self.data = data
        self.error_code = error_code
        self.is_retriable = is_retriable

def execute_storage_operation(operation_type, simulate_condition):
    """
    Typed error semantics:
      - Empty result (records not found) is a SUCCESSFUL status with empty list (NOT an error).
      - Network timeout / socket hangup is RETRIABLE.
      - Tenant authorization violation or schema mismatch is TERMINAL (never retried).
    """
    if simulate_condition == "empty_match":
        # Successful query returning zero matching vectors
        return StorageResult(status="ok", data=[])
        
    elif simulate_condition == "connection_timeout":
        # Database socket timed out (transient network glitch)
        return StorageResult(status="error", error_code="TIMEOUT", is_retriable=True)

    elif simulate_condition == "tenant_forbidden":
        # Cross-tenant access attempt
        return StorageResult(status="error", error_code="FORBIDDEN", is_retriable=False)
        
    elif simulate_condition == "success":
        return StorageResult(status="ok", data=[{"id": "doc_1", "score": 0.89}])

# 1. Empty match: valid query, zero hits (should not trigger retry or error alerts!)
res_empty = execute_storage_operation("search", "empty_match")
assert res_empty.status == "ok" and len(res_empty.data) == 0

# 2. Storage timeout: retriable transient error
res_timeout = execute_storage_operation("search", "connection_timeout")
assert res_timeout.status == "error" and res_timeout.is_retriable is True

# 3. Security violation: terminal error (must fail fast without retry loop)
res_forbidden = execute_storage_operation("search", "tenant_forbidden")
assert res_forbidden.status == "error" and res_forbidden.is_retriable is False

print(f"Storage error semantics verified: empty_is_ok={res_empty.status == 'ok'}, timeout_retriable={res_timeout.is_retriable}, forbidden_retriable={res_forbidden.is_retriable}")
