"""Cryptographic JWT validation, token lifetime verification, audience enforcement, and revocation blocklists.

Demonstrates:
1. Cryptographic HMAC-SHA256 signature verification rejecting forged tokens and the insecure 'none' algorithm.
2. Strict lifetime validation: Verifying not-before (nbf) and expiration (exp) with bounded clock skew.
3. Issuer and Audience ('aud') checks to defeat Confused Deputy attacks across microservices.
4. Distributed token revocation cache (blocklist) to handle immediate credential revocation and logout.
"""
from typing import Any, Dict, List, Optional, Set
import hashlib
import hmac
import json
import time

class JwtValidationError(Exception):
    pass

class ProductionJwtValidator:
    def __init__(self, secret_key: bytes, expected_issuer: str, expected_audience: str, allowed_clock_skew_seconds: int = 5):
        self.secret_key = secret_key
        self.expected_issuer = expected_issuer
        self.expected_audience = expected_audience
        self.clock_skew = allowed_clock_skew_seconds
        # Simulated distributed Redis blocklist for revoked token IDs (jti)
        self._revocation_store: Set[str] = set()

    def revoke_token(self, jti: str) -> None:
        self._revocation_store.add(jti)

    def validate_and_decode(self, token_str: str) -> Dict[str, Any]:
        parts = token_str.split(".")
        if len(parts) != 3:
            raise JwtValidationError("Malformed JWT: Must contain exactly 3 segments (header.payload.signature).")

        header_b64, payload_b64, sig_b64 = parts

        # 1. Decode header and enforce algorithm allowlist
        try:
            header = json.loads(bytes.fromhex(header_b64).decode("utf-8"))
        except Exception:
            raise JwtValidationError("Header is not valid JSON.")

        alg = header.get("alg")
        if alg != "HS256":
            raise JwtValidationError(f"Insecure or unsupported algorithm '{alg}'. Only HS256 is permitted.")

        # 2. Cryptographic signature check (using constant-time compare)
        signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
        expected_sig = hmac.new(self.secret_key, signing_input, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig_b64, expected_sig):
            raise JwtValidationError("Cryptographic signature verification failed: Token was forged or tampered with.")

        # 3. Decode payload
        try:
            payload = json.loads(bytes.fromhex(payload_b64).decode("utf-8"))
        except Exception:
            raise JwtValidationError("Payload is not valid JSON.")

        now = time.time()

        # 4. Expiration check (exp)
        exp = payload.get("exp")
        if exp is None or not isinstance(exp, (int, float)):
            raise JwtValidationError("Missing or invalid 'exp' claim.")
        if now > (exp + self.clock_skew):
            raise JwtValidationError(f"Token expired at {exp}, current time is {int(now)}.")

        # 5. Not-before check (nbf)
        nbf = payload.get("nbf")
        if nbf is not None and now < (nbf - self.clock_skew):
            raise JwtValidationError(f"Token not valid before {nbf}, current time is {int(now)}.")

        # 6. Issuer check (iss)
        iss = payload.get("iss")
        if iss != self.expected_issuer:
            raise JwtValidationError(f"Issuer mismatch: Expected '{self.expected_issuer}', got '{iss}'.")

        # 7. CRITICAL AUDIENCE CHECK (aud) - Defends against Confused Deputy Attack!
        aud = payload.get("aud")
        if aud != self.expected_audience:
            raise JwtValidationError(f"Audience mismatch: Expected '{self.expected_audience}', got '{aud}'.")

        # 8. Revocation check (jti)
        jti = payload.get("jti")
        if jti and jti in self._revocation_store:
            raise JwtValidationError(f"Token '{jti}' has been explicitly revoked or logged out.")

        return payload

def mint_token(secret_key: bytes, claims: Dict[str, Any]) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    h_hex = json.dumps(header).encode("utf-8").hex()
    p_hex = json.dumps(claims).encode("utf-8").hex()
    sig = hmac.new(secret_key, f"{h_hex}.{p_hex}".encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{h_hex}.{p_hex}.{sig}"

if __name__ == "__main__":
    secret = b"k9_production_hmac_secret_key_32bytes"
    validator = ProductionJwtValidator(
        secret_key=secret,
        expected_issuer="https://auth.company.com",
        expected_audience="https://api.company.com/rag-service"
    )

    now = time.time()

    # 1. Valid token passes
    valid_claims = {
        "sub": "user_42",
        "tenant_id": "tenant_enterprise",
        "iss": "https://auth.company.com",
        "aud": "https://api.company.com/rag-service",
        "exp": now + 3600,
        "nbf": now - 10,
        "jti": "token_uuid_001",
        "scopes": ["documents:read", "search:execute"]
    }
    token = mint_token(secret, valid_claims)
    decoded = validator.validate_and_decode(token)
    assert decoded["sub"] == "user_42"
    assert decoded["tenant_id"] == "tenant_enterprise"

    # 2. Tampered signature rejected
    tampered = token[:-4] + "ffff"
    try:
        validator.validate_and_decode(tampered)
        assert False, "Should reject tampered signature"
    except JwtValidationError as e:
        assert "signature verification failed" in str(e)

    # 3. Confused Deputy Attack: Token minted for different audience rejected
    wrong_aud_claims = dict(valid_claims, aud="https://api.company.com/public-billing")
    wrong_aud_token = mint_token(secret, wrong_aud_claims)
    try:
        validator.validate_and_decode(wrong_aud_token)
        assert False, "Should reject wrong audience"
    except JwtValidationError as e:
        assert "Audience mismatch" in str(e)

    # 4. Expired token rejected
    expired_claims = dict(valid_claims, exp=now - 100)
    expired_token = mint_token(secret, expired_claims)
    try:
        validator.validate_and_decode(expired_token)
        assert False, "Should reject expired token"
    except JwtValidationError as e:
        assert "Token expired" in str(e)

    # 5. Revocation / Logout enforcement
    validator.revoke_token("token_uuid_001")
    try:
        validator.validate_and_decode(token)
        assert False, "Should reject revoked token"
    except JwtValidationError as e:
        assert "explicitly revoked" in str(e)

    print("Production JWT signature, audience, and revocation validation verified successfully.")
