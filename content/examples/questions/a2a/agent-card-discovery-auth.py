"""Agent Card Discovery vs Runtime Cryptographic Authorization and Scoped Delegation.

Demonstrates:
1. Agent Card Discovery Metadata:
   - Public declarative card advertising protocol version, capabilities, schema, endpoints, and auth methods.
   - Proves discovery != authorization: reading the card confers zero permission to invoke tools.
2. Runtime User Delegation Token:
   - Coordinator mints an HMAC-signed delegated JWT carrying subject (user), issuer, audience,
     downscoped permissions (e.g. "audit:read"), and short-lived expiration.
3. Perimeter Gate:
   - Specialist verifies token signature, exact audience match (defeating confused-deputy attacks),
     and enforces scope boundaries before accepting execution.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import hmac
import json
import time
from typing import Any, Dict, List, Optional, Set


# --- 1. Declarative Agent Card ---
AGENT_CARD = {
    "$schema": "https://a2a-protocol.org/v1/agent-card.json",
    "name": "corporate-security-auditor",
    "version": "1.4.0",
    "description": "Autonomous security compliance auditor specialized in SOC2 and IAM policy verification.",
    "endpoint_url": "https://security-specialist.corp.internal/a2a/v1",
    "supported_protocols": ["A2A-HTTP-JSON", "A2A-SSE"],
    "authentication": {
        "type": "oauth2_bearer",
        "token_endpoint": "https://auth.corp.internal/oauth/token",
        "required_audience": "https://security-specialist.corp.internal"
    },
    "capabilities": [
        {
            "name": "audit_iam_roles",
            "required_scope": "iam:audit:read",
            "input_schema": {
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "account_ids": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["tenant_id", "account_ids"]
            }
        },
        {
            "name": "revoke_excessive_keys",
            "required_scope": "iam:keys:revoke",
            "input_schema": {
                "type": "object",
                "properties": {
                    "key_id": {"type": "string"}
                },
                "required": ["key_id"]
            }
        }
    ]
}


# --- 2. Token Minting and Delegation ---
SHARED_HMAC_SECRET = b"production-secure-cluster-shared-secret-key-4096"


def mint_delegated_token(
    user_id: str,
    issuer: str,
    audience: str,
    scopes: List[str],
    ttl_seconds: int = 60
) -> str:
    """Mints an HMAC-SHA256 authenticated delegation token."""
    header = {"alg": "HS256", "typ": "JWT"}
    now = int(time.time())
    payload = {
        "sub": user_id,
        "iss": issuer,
        "aud": audience,
        "scopes": scopes,
        "iat": now,
        "exp": now + ttl_seconds
    }

    header_b64 = json.dumps(header).encode("utf-8").hex()
    payload_b64 = json.dumps(payload).encode("utf-8").hex()
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")

    sig = hmac.new(SHARED_HMAC_SECRET, signing_input, hashlib.sha256).hexdigest()
    return f"{header_b64}.{payload_b64}.{sig}"


# --- 3. Specialist Endpoint Enforcing Perimeter Auth ---
class RemoteSpecialistServer:
    """Specialist agent endpoint enforcing strict audience and delegated scope validation."""

    def __init__(self, agent_card: Dict[str, Any]):
        self.card = agent_card
        self.expected_audience = agent_card["authentication"]["required_audience"]

    def verify_token(self, token: str) -> Dict[str, Any]:
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Malformed token format")

        header_b64, payload_b64, signature = parts
        signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
        expected_sig = hmac.new(SHARED_HMAC_SECRET, signing_input, hashlib.sha256).hexdigest()

        if not hmac.compare_digest(signature, expected_sig):
            raise PermissionError("Cryptographic signature mismatch")

        payload = json.loads(bytes.fromhex(payload_b64).decode("utf-8"))
        now = int(time.time())

        # Check expiration
        if now > payload["exp"]:
            raise PermissionError(f"Token expired at {payload['exp']}, current time: {now}")

        # Check audience to defeat confused-deputy attacks
        if payload["aud"] != self.expected_audience:
            raise PermissionError(f"Audience mismatch: expected '{self.expected_audience}', got '{payload['aud']}'")

        return payload

    def invoke_capability(self, token: Optional[str], capability_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        # 1. Require token (Discovery card does not authorize execution!)
        if not token:
            raise PermissionError("401 Unauthorized: Bearer delegation token required for capability execution")

        # 2. Validate token claims
        claims = self.verify_token(token)

        # 3. Find capability in declared card
        cap_def = next((c for c in self.card["capabilities"] if c["name"] == capability_name), None)
        if not cap_def:
            raise KeyError(f"Capability '{capability_name}' not supported by agent")

        # 4. Check delegated scope
        required_scope = cap_def["required_scope"]
        user_scopes = set(claims.get("scopes", []))
        if required_scope not in user_scopes:
            raise PermissionError(
                f"403 Forbidden: Missing required scope '{required_scope}'. Granted: {user_scopes}"
            )

        # Execute capability safely
        return {
            "status": "SUCCESS",
            "capability": capability_name,
            "invoker": claims["sub"],
            "result": f"Executed {capability_name} for tenant {args.get('tenant_id') or 'N/A'}"
        }


def main():
    specialist_server = RemoteSpecialistServer(AGENT_CARD)

    # 1. Test Discovery Card: Public inspection works without token
    print("1. Discovery Metadata Inspection:")
    print(f"  Agent Name: {AGENT_CARD['name']}")
    print(f"  Capabilities: {[c['name'] for c in AGENT_CARD['capabilities']]}")
    print(f"  Auth Scheme: {AGENT_CARD['authentication']['type']}")

    # 2. Test Invoking without Token -> Fails (Proves Discovery != Authorization)
    print("\n2. Invoking without Authentication Token:")
    try:
        specialist_server.invoke_capability(
            token=None,
            capability_name="audit_iam_roles",
            args={"tenant_id": "tenant_12", "account_ids": ["acc_99"]}
        )
        assert False, "Invocation without token must fail"
    except PermissionError as err:
        print(f"  Successfully blocked unauthenticated invocation: {err}")

    # 3. Test Confused-Deputy Attack (Valid signature, wrong audience)
    print("\n3. Testing Audience Verification (Confused-Deputy Defense):")
    foreign_audience_token = mint_delegated_token(
        user_id="alice@corp.com",
        issuer="coordinator-agent",
        audience="https://billing-service.corp.internal",  # Wrong audience!
        scopes=["iam:audit:read"]
    )
    try:
        specialist_server.invoke_capability(
            token=foreign_audience_token,
            capability_name="audit_iam_roles",
            args={"tenant_id": "tenant_12", "account_ids": ["acc_99"]}
        )
        assert False, "Token for wrong audience must be rejected"
    except PermissionError as err:
        print(f"  Successfully blocked wrong-audience token: {err}")

    # 4. Test Scope Enforcement (Read-only token attempting key revocation)
    print("\n4. Testing Downscoped Delegation Enforcement:")
    readonly_token = mint_delegated_token(
        user_id="alice@corp.com",
        issuer="coordinator-agent",
        audience="https://security-specialist.corp.internal",
        scopes=["iam:audit:read"]  # Missing iam:keys:revoke!
    )
    try:
        specialist_server.invoke_capability(
            token=readonly_token,
            capability_name="revoke_excessive_keys",
            args={"key_id": "KEY_88192"}
        )
        assert False, "Readonly token must not be allowed to revoke keys"
    except PermissionError as err:
        print(f"  Successfully blocked out-of-scope mutation: {err}")

    # 5. Test Successful Execution with Matching Scoped Token
    print("\n5. Authorized Execution with Downscoped Token:")
    res = specialist_server.invoke_capability(
        token=readonly_token,
        capability_name="audit_iam_roles",
        args={"tenant_id": "tenant_12", "account_ids": ["acc_99"]}
    )
    print(f"  Execution result: {res['status']} by {res['invoker']}")
    assert res["status"] == "SUCCESS"
    assert res["invoker"] == "alice@corp.com"

    print("\nAgent Card discovery vs cryptographic authorization verified successfully.")


if __name__ == "__main__":
    main()
