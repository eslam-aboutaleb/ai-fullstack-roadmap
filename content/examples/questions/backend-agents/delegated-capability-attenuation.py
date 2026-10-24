# /// script
# dependencies = []
# ///
"""
Cryptographic Capability Attenuation for Cross-Service Agent Delegation.

Demonstrates:
1. Down-scoping broad orchestrator authority into an attenuated sub-token
   (restricting tenant, resource path, action, and time-to-live).
2. Preventing ambient authority privilege escalation when an agent delegates
   tasks to downstream specialist microservices.
3. Rejecting unauthorized cross-resource reads and write escalations.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from typing import Any, Dict, List, Optional, Tuple


class DelegationTokenAuthority:
    """Mints and verifies cryptographically signed attenuated capability tokens."""

    def __init__(self, signing_secret: str) -> None:
        self.secret = signing_secret.encode("utf-8")

    def mint_attenuated_token(
        self,
        tenant_id: str,
        delegated_to_agent: str,
        permitted_resource: str,
        permitted_actions: List[str],
        ttl_seconds: int = 30,
    ) -> str:
        """Derives a restricted capability token with explicit scope caveats."""
        payload = {
            "tenant_id": tenant_id,
            "delegated_to": delegated_to_agent,
            "resource": permitted_resource,
            "actions": permitted_actions,
            "expires_at": time.time() + ttl_seconds,
            "nonce": hashlib.sha256(f"{time.time()}:{permitted_resource}".encode()).hexdigest()[:12],
        }
        serialized = json.dumps(payload, sort_keys=True)
        signature = hmac.new(self.secret, serialized.encode("utf-8"), hashlib.sha256).hexdigest()
        token_envelope = {"payload": payload, "signature": signature}
        return json.dumps(token_envelope)

    def verify_and_decode(self, raw_token: str) -> Optional[Dict[str, Any]]:
        try:
            envelope = json.loads(raw_token)
            payload = envelope["payload"]
            expected_sig = envelope["signature"]
            serialized = json.dumps(payload, sort_keys=True)
            calculated_sig = hmac.new(self.secret, serialized.encode("utf-8"), hashlib.sha256).hexdigest()

            if not hmac.compare_digest(expected_sig, calculated_sig):
                return None  # Signature tampered

            if time.time() > payload.get("expires_at", 0):
                return None  # Token expired

            return payload
        except Exception:
            return None


class DownstreamDocumentService:
    """Protected microservice enforcing capability attenuation checks."""

    def __init__(self, authority: DelegationTokenAuthority) -> None:
        self.authority = authority
        self._datastore: Dict[str, Dict[str, str]] = {
            "tenant-alpha:docs/public_report": {"title": "Annual Review", "content": "Fiscal year 2026 was solid."},
            "tenant-alpha:docs/payroll_records": {"title": "Salaries", "content": "CONFIDENTIAL EXECUTIVE PAYROLL."},
            "tenant-beta:docs/public_report": {"title": "Beta Ops", "content": "Beta partner data."},
        }

    def execute_operation(
        self,
        raw_token: str,
        tenant_id: str,
        resource_path: str,
        action: str,
    ) -> Tuple[int, Dict[str, Any]]:
        # 1. Cryptographic token verification
        claims = self.authority.verify_and_decode(raw_token)
        if not claims:
            return 401, {"error": "UNAUTHORIZED", "message": "Invalid or expired capability token"}

        # 2. Tenant isolation check
        if claims.get("tenant_id") != tenant_id:
            return 403, {"error": "TENANT_MISMATCH", "message": "Token not valid for target tenant"}

        # 3. Resource capability boundary check
        if claims.get("resource") != resource_path:
            return 403, {
                "error": "RESOURCE_SCOPE_EXCEEDED",
                "message": f"Token authority limited to '{claims.get('resource')}', cannot access '{resource_path}'",
            }

        # 4. Action capability check
        if action not in claims.get("actions", []):
            return 403, {
                "error": "ACTION_NOT_PERMITTED",
                "message": f"Action '{action}' exceeds permitted actions {claims.get('actions')}",
            }

        # 5. Authoritative data access
        key = f"{tenant_id}:{resource_path}"
        data = self._datastore.get(key)
        if not data:
            return 404, {"error": "NOT_FOUND", "message": "Resource not found"}

        return 200, {"status": "SUCCESS", "data": data}


def main() -> None:
    secret = "k_secret_cluster_hmac_signing_key_9981"
    authority = DelegationTokenAuthority(signing_secret=secret)
    document_service = DownstreamDocumentService(authority)

    tenant = "tenant-alpha"
    permitted_doc = "docs/public_report"
    sensitive_doc = "docs/payroll_records"

    # Orchestrator delegates to a third-party Summarizer Agent.
    # Instead of sending root ambient credentials, it mints an attenuated sub-token:
    attenuated_token = authority.mint_attenuated_token(
        tenant_id=tenant,
        delegated_to_agent="summarizer-specialist-v1",
        permitted_resource=permitted_doc,
        permitted_actions=["read"],
        ttl_seconds=30,
    )

    # 1. Permitted Action: Summarizer reads permitted document
    status_1, resp_1 = document_service.execute_operation(
        raw_token=attenuated_token,
        tenant_id=tenant,
        resource_path=permitted_doc,
        action="read",
    )
    assert status_1 == 200, f"Expected 200, got {status_1}"
    assert "Annual Review" in resp_1["data"]["title"]
    permitted_read = True

    # 2. Forbidden Escalation 1: Prompt injection in public_report attempts to access payroll_records
    status_2, resp_2 = document_service.execute_operation(
        raw_token=attenuated_token,
        tenant_id=tenant,
        resource_path=sensitive_doc,
        action="read",
    )
    assert status_2 == 403, f"Expected 403 Forbidden for cross-resource access, got {status_2}"
    assert resp_2["error"] == "RESOURCE_SCOPE_EXCEEDED"
    forbidden_cross_doc = status_2

    # 3. Forbidden Escalation 2: Attenuated token attempts to execute write action
    status_3, resp_3 = document_service.execute_operation(
        raw_token=attenuated_token,
        tenant_id=tenant,
        resource_path=permitted_doc,
        action="write",
    )
    assert status_3 == 403, f"Expected 403 Forbidden for write action, got {status_3}"
    assert resp_3["error"] == "ACTION_NOT_PERMITTED"
    forbidden_action = status_3

    # 4. Forbidden Escalation 3: Cross-tenant attack
    status_4, resp_4 = document_service.execute_operation(
        raw_token=attenuated_token,
        tenant_id="tenant-beta",
        resource_path=permitted_doc,
        action="read",
    )
    assert status_4 == 403
    assert resp_4["error"] == "TENANT_MISMATCH"

    # 5. Tampered token rejection
    tampered_token = attenuated_token.replace("public_report", "payroll_records")
    status_5, resp_5 = document_service.execute_operation(
        raw_token=tampered_token,
        tenant_id=tenant,
        resource_path=sensitive_doc,
        action="read",
    )
    assert status_5 == 401
    assert resp_5["error"] == "UNAUTHORIZED"

    print(
        f"Delegated capability attenuation verified: permitted_read={permitted_read}, "
        f"forbidden_cross_doc={forbidden_cross_doc}, forbidden_action={forbidden_action}"
    )


if __name__ == "__main__":
    main()
