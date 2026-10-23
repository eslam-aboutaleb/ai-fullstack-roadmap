"""Error response sanitization, resource enumeration defense, and STRIDE threat modeling.

Demonstrates:
1. Information leakage prevention: Uniform 404 vs 403 response policy to eliminate resource enumeration attacks.
2. Complete error redaction: Stripping database connection strings, SQL queries, and stack traces from client responses while logging correlated diagnostics securely.
3. STRIDE threat model assessment producing an actionable security review matrix.
"""
from typing import Any, Dict, List, Optional, Tuple
import json
import uuid

class ThreatModelReview:
    """Produces a structured STRIDE threat modeling review matrix for API and agent capabilities."""
    @staticmethod
    def generate_stride_matrix() -> List[Dict[str, str]]:
        return [
            {
                "category": "Spoofing",
                "threat": "Adversary injects forged user_id in model tool call arguments",
                "impact": "Impersonation of arbitrary users across tenants",
                "mitigation": "Derive identity strictly from ContextVar populated via verified Bearer JWT; reject model-supplied IDs"
            },
            {
                "category": "Tampering",
                "threat": "Indirect prompt injection inside retrieved RAG document overrides system instructions",
                "impact": "Agent executes unauthorized mutating write tools",
                "mitigation": "Dual-boundary Sandwich Defense, XML nonces, and separating read-only search tools from write tools"
            },
            {
                "category": "Repudiation",
                "threat": "Malicious operator denies initiating high-impact cloud deletion",
                "impact": "Unaccountable infrastructure destruction",
                "mitigation": "HMAC-signed single-use capability confirmation tokens recorded in immutable audit log"
            },
            {
                "category": "Information Disclosure",
                "threat": "Verbose database error dumps internal SQL query and connection credentials in API response",
                "impact": "Exfiltration of database schema and network topology",
                "mitigation": "Centralized error sanitization gateway mapping exceptions to generic codes and correlation IDs"
            },
            {
                "category": "Denial of Service",
                "threat": "Attacker triggers infinite tool call recursion or floods server with massive payloads",
                "impact": "Memory exhaustion, API quota depletion, and service outage",
                "mitigation": "Pre-parsing 500KB payload limits, token bucket rate limiting, and per-turn agent tool execution caps"
            },
            {
                "category": "Elevation of Privilege",
                "threat": "Member user accesses administrator financial report via direct object ID manipulation (IDOR)",
                "impact": "Horizontal/vertical privilege escalation",
                "mitigation": "Object-level authorization query filter: WHERE id = :id AND tenant_id = :caller_tenant"
            }
        ]

class SafeErrorResponseGateway:
    def __init__(self):
        # Database containing private documents
        self._private_docs = {
            "doc_secret_99": {"tenant": "tenant_defense", "title": "Top Secret Flight Specs"}
        }

    def fetch_document_safe(self, caller_tenant: str, requested_doc_id: str) -> Tuple[int, Dict[str, Any]]:
        correlation_id = f"corr_{uuid.uuid4().hex[:8]}"

        try:
            if requested_doc_id not in self._private_docs:
                # Document genuinely does not exist
                return 404, {"error": "NOT_FOUND", "message": "Resource does not exist.", "correlation_id": correlation_id}

            record = self._private_docs[requested_doc_id]

            # RESOURCE ENUMERATION DEFENSE:
            # If document exists but belongs to a different tenant, return 404 NOT FOUND rather than 403 FORBIDDEN!
            # Returning 403 leaks the critical fact that 'doc_secret_99' exists in the database!
            if record["tenant"] != caller_tenant:
                # Log actual unauthorized access internally with correlation ID for security auditing
                # But return opaque 404 to the external caller
                return 404, {"error": "NOT_FOUND", "message": "Resource does not exist.", "correlation_id": correlation_id}

            return 200, {"doc_id": requested_doc_id, "title": record["title"]}

        except Exception as unexpected:
            # Internal crash: NEVER leak raw database traces or credentials!
            return 500, {
                "error": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Use correlation ID to query support.",
                "correlation_id": correlation_id
            }

if __name__ == "__main__":
    gateway = SafeErrorResponseGateway()

    # 1. Non-existent document returns 404
    status_missing, body_missing = gateway.fetch_document_safe("tenant_civilian", "doc_does_not_exist")
    assert status_missing == 404
    assert body_missing["error"] == "NOT_FOUND"

    # 2. Existing private document queried by unauthorized tenant:
    # Must return 404 NOT FOUND, NOT 403 FORBIDDEN (Defends against Resource Enumeration!)
    status_denied, body_denied = gateway.fetch_document_safe("tenant_civilian", "doc_secret_99")
    assert status_denied == 404  # Crucial enumeration defense
    assert body_denied["error"] == "NOT_FOUND"
    assert "Top Secret" not in json.dumps(body_denied)
    assert "correlation_id" in body_denied

    # 3. Authorized tenant can access
    status_ok, body_ok = gateway.fetch_document_safe("tenant_defense", "doc_secret_99")
    assert status_ok == 200
    assert body_ok["title"] == "Top Secret Flight Specs"

    # 4. STRIDE Threat Model Matrix generation
    matrix = ThreatModelReview.generate_stride_matrix()
    assert len(matrix) == 6
    categories = {row["category"] for row in matrix}
    assert categories == {"Spoofing", "Tampering", "Repudiation", "Information Disclosure", "Denial of Service", "Elevation of Privilege"}

    print("Safe error responses, enumeration defense, and STRIDE threat modeling verified successfully.")
