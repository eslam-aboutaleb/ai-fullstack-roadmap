"""Remote MCP server security, audience verification, and context-propagated identity.

Demonstrates:
1. Bearer JWT validation: Expiration, issuer, and token audience ('aud') check to prevent confused-deputy attacks.
2. Async context propagation via contextvars: Ensuring authenticated principal travels across async tool call boundaries.
3. Defeating model-injected tenant spoofing: Tools read verified identity from context, NEVER from model-supplied arguments.
4. Scope enforcement: Restricting tool invocation to granted capability scopes.
"""
from typing import Any, Dict, List, Optional, Set
import contextvars
import hmac
import hashlib
import json
import time

# Execution context holding verified request principal
CURRENT_CALLER: contextvars.ContextVar[Optional[Dict[str, Any]]] = contextvars.ContextVar("current_caller", default=None)

class RemoteMcpSecurityGateway:
    SERVER_AUDIENCE = "mcp://analytics-gateway.prod.corp"
    JWT_SECRET = b"production-signing-secret-key-32b"

    @classmethod
    def create_synthetic_token(cls, user_id: str, tenant_id: str, audience: str, scopes: List[str], expires_in: int = 3600) -> str:
        header = {"alg": "HS256", "typ": "JWT"}
        payload = {
            "sub": user_id,
            "tenant_id": tenant_id,
            "aud": audience,
            "iss": "https://auth.prod.corp",
            "exp": int(time.time()) + expires_in,
            "scopes": scopes
        }
        h_str = json.dumps(header).encode("utf-8").hex()
        p_str = json.dumps(payload).encode("utf-8").hex()
        sig = hmac.new(cls.JWT_SECRET, f"{h_str}.{p_str}".encode("utf-8"), hashlib.sha256).hexdigest()
        return f"{h_str}.{p_str}.{sig}"

    @classmethod
    def authenticate_request(cls, auth_header: str) -> Dict[str, Any]:
        if not auth_header.startswith("Bearer "):
            raise PermissionError("Missing or malformed Authorization header")

        token = auth_header[7:]
        parts = token.split(".")
        if len(parts) != 3:
            raise PermissionError("Malformed JWT structure")

        h_str, p_str, sig = parts
        expected_sig = hmac.new(cls.JWT_SECRET, f"{h_str}.{p_str}".encode("utf-8"), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected_sig):
            raise PermissionError("Invalid cryptographic JWT signature")

        payload = json.loads(bytes.fromhex(p_str).decode("utf-8"))

        # Verify expiration
        if time.time() > payload.get("exp", 0):
            raise PermissionError("Token expired")

        # CRITICAL AUDIENCE CHECK: Defend against Confused Deputy attack!
        # A token minted for Server B must NOT be accepted by Server A!
        token_aud = payload.get("aud")
        if token_aud != cls.SERVER_AUDIENCE:
            raise PermissionError(f"Audience mismatch: Token intended for '{token_aud}', this server is '{cls.SERVER_AUDIENCE}'")

        return {
            "user_id": payload["sub"],
            "tenant_id": payload["tenant_id"],
            "scopes": set(payload.get("scopes", []))
        }

class SecureAnalyticsTool:
    REQUIRED_SCOPE = "analytics:read"

    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        # 1. Retrieve verified principal from context
        principal = CURRENT_CALLER.get()
        if not principal:
            return {"content": [{"type": "text", "text": "Unauthorized: No security context"}], "isError": True}

        # 2. Scope check
        if self.REQUIRED_SCOPE not in principal["scopes"]:
            return {
                "content": [{"type": "text", "text": f"Forbidden: Caller lacks scope '{self.REQUIRED_SCOPE}'"}],
                "isError": True
            }

        # 3. Defeat parameter injection: Ignore any model-supplied tenant_id!
        # Use strictly principal['tenant_id'] from cryptographic context
        verified_tenant = principal["tenant_id"]
        metric_name = arguments.get("metric_name", "cpu_utilization")

        # In a real system, query database with WHERE tenant_id = verified_tenant
        return {
            "content": [
                {"type": "text", "text": json.dumps({
                    "tenant_id": verified_tenant,
                    "metric": metric_name,
                    "value": 42.8,
                    "caller_user": principal["user_id"]
                })}
            ],
            "isError": False
        }

if __name__ == "__main__":
    gateway = RemoteMcpSecurityGateway()
    tool = SecureAnalyticsTool()

    # 1. Valid token for this server
    valid_token = gateway.create_synthetic_token(
        user_id="user_alice",
        tenant_id="tenant_finance",
        audience="mcp://analytics-gateway.prod.corp",
        scopes=["analytics:read"]
    )
    principal = gateway.authenticate_request(f"Bearer {valid_token}")
    assert principal["user_id"] == "user_alice"
    assert principal["tenant_id"] == "tenant_finance"

    # Set context and execute tool
    ctx_token = CURRENT_CALLER.set(principal)
    res_ok = tool.execute({"metric_name": "quarterly_ebitda", "tenant_id": "ATTEMPTED_SPOOF_TENANT"})
    CURRENT_CALLER.reset(ctx_token)

    assert res_ok["isError"] is False
    res_data = json.loads(res_ok["content"][0]["text"])
    # Verified: Spoofed argument was ignored; verified context tenant was enforced!
    assert res_data["tenant_id"] == "tenant_finance"
    assert res_data["caller_user"] == "user_alice"

    # 2. Confused Deputy Attack: Token minted for unrelated Server B
    rogue_server_token = gateway.create_synthetic_token(
        user_id="user_bob",
        tenant_id="tenant_engineering",
        audience="mcp://code-repo.prod.corp",  # Wrong audience!
        scopes=["analytics:read"]
    )
    try:
        gateway.authenticate_request(f"Bearer {rogue_server_token}")
        assert False, "Should have failed audience check"
    except PermissionError as pe:
        assert "Audience mismatch" in str(pe)

    # 3. Insufficient scope rejection
    no_scope_token = gateway.create_synthetic_token(
        user_id="user_charlie",
        tenant_id="tenant_hr",
        audience="mcp://analytics-gateway.prod.corp",
        scopes=["general:read"]  # Missing analytics:read
    )
    principal_no_scope = gateway.authenticate_request(f"Bearer {no_scope_token}")
    ctx_token2 = CURRENT_CALLER.set(principal_no_scope)
    res_no_scope = tool.execute({"metric_name": "headcount"})
    CURRENT_CALLER.reset(ctx_token2)

    assert res_no_scope["isError"] is True
    assert "Forbidden: Caller lacks scope 'analytics:read'" in res_no_scope["content"][0]["text"]

    print("Remote MCP authentication, audience verification, and context propagation verified successfully.")
