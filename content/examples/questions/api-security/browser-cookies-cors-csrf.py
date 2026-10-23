"""Browser security controls: Cookie attributes, CORS preflight policies, and CSRF token defenses.

Demonstrates:
1. Hardened cookie controls: HttpOnly (blocks XSS exfiltration), Secure (forces HTTPS), SameSite=Lax/Strict (mitigates ambient CSRF).
2. CORS preflight engine: Handling OPTIONS requests, validating Origin allowlists, and managing Access-Control headers.
3. The fundamental invariant: CORS is a browser read-boundary, NOT backend execution authorization (non-browser clients bypass CORS).
4. Synchronizer anti-CSRF token validation for state-mutating HTTP methods.
"""
from typing import Any, Dict, List, Optional, Set, Tuple

class BrowserSecurityEngine:
    ALLOWED_ORIGINS: Set[str] = {
        "https://app.enterprise.com",
        "https://admin.enterprise.com"
    }

    @staticmethod
    def build_session_cookie(name: str, value: str, max_age: int = 86400, samesite: str = "Lax") -> str:
        """Constructs an RFC 6265 hardened Set-Cookie header."""
        parts = [
            f"{name}={value}",
            f"Max-Age={max_age}",
            "Path=/",
            "HttpOnly",      # Prevents JavaScript document.cookie access (mitigates XSS exfiltration)
            "Secure",        # Transmitted exclusively over TLS
            f"SameSite={samesite}"  # Restricts cross-site request inclusion (mitigates CSRF)
        ]
        return "; ".join(parts)

    @classmethod
    def handle_cors_preflight(cls, origin: Optional[str], requested_method: str) -> Tuple[int, Dict[str, str]]:
        """Handles HTTP OPTIONS preflight request."""
        if not origin or origin not in cls.ALLOWED_ORIGINS:
            # Origin not allowed: Do NOT return Access-Control-Allow-Origin header
            return 403, {"Content-Type": "text/plain"}

        headers = {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Authorization, Content-Type, X-CSRF-Token",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Max-Age": "86400"
        }
        return 204, headers

    @classmethod
    def process_api_request(
        cls,
        method: str,
        origin: Optional[str],
        session_cookie: Optional[str],
        csrf_header: Optional[str],
        expected_csrf_token: str
    ) -> Tuple[int, str]:
        # 1. CORS Response-Reading Boundary Check (for browser callers)
        cors_permitted = origin in cls.ALLOWED_ORIGINS if origin else True

        # 2. Authentication check
        if not session_cookie or not session_cookie.startswith("sess_"):
            return 401, "Unauthorized: Invalid or missing session cookie"

        # 3. CSRF Protection for state-mutating requests (POST, PUT, DELETE)
        if method in {"POST", "PUT", "DELETE"}:
            if not csrf_header or csrf_header != expected_csrf_token:
                return 403, "Forbidden: Invalid or missing anti-CSRF token"

        # 4. Backend business mutation succeeds
        response_text = f"Action {method} executed successfully."
        return 200, response_text

if __name__ == "__main__":
    engine = BrowserSecurityEngine()

    # 1. Hardened cookie syntax
    cookie_hdr = engine.build_session_cookie("auth_session", "sess_991823", samesite="Lax")
    assert "HttpOnly" in cookie_hdr
    assert "Secure" in cookie_hdr
    assert "SameSite=Lax" in cookie_hdr

    # 2. CORS Preflight Allowed
    status, headers = engine.handle_cors_preflight("https://app.enterprise.com", "POST")
    assert status == 204
    assert headers["Access-Control-Allow-Origin"] == "https://app.enterprise.com"

    # 3. CORS Preflight Blocked for untrusted origin
    status_bad, headers_bad = engine.handle_cors_preflight("https://evil-phishing.com", "POST")
    assert status_bad == 403
    assert "Access-Control-Allow-Origin" not in headers_bad

    # 4. CSRF Protection on Mutating POST: Missing CSRF header fails even with valid cookie!
    post_status, msg = engine.process_api_request(
        method="POST",
        origin="https://app.enterprise.com",
        session_cookie="sess_991823",
        csrf_header=None,
        expected_csrf_token="secret_csrf_token_abc"
    )
    assert post_status == 403
    assert "anti-CSRF" in msg

    # 5. Valid Mutation with both Session Cookie AND matching CSRF header
    post_ok_status, msg_ok = engine.process_api_request(
        method="POST",
        origin="https://app.enterprise.com",
        session_cookie="sess_991823",
        csrf_header="secret_csrf_token_abc",
        expected_csrf_token="secret_csrf_token_abc"
    )
    assert post_ok_status == 200
    assert "executed successfully" in msg_ok

    # 6. Critical Proof: Non-browser client (no origin header, e.g. curl) can invoke if credentials supplied
    curl_status, curl_msg = engine.process_api_request(
        method="GET",
        origin=None,
        session_cookie="sess_991823",
        csrf_header=None,
        expected_csrf_token="secret_csrf_token_abc"
    )
    assert curl_status == 200

    print("Browser cookie controls, CORS preflight, and CSRF token defenses verified successfully.")
