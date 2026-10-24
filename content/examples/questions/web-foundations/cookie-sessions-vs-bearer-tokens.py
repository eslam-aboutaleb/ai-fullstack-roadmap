"""Demonstrate Cookie sessions (CSRF risk, XSS protected) vs Bearer tokens (XSS risk, CSRF immune)."""

class SecurityContextSimulator:
    def __init__(self):
        # Server-side active session store
        self.sessions = {"sess_cookie_123": {"user_id": "usr_alice", "tenant": "acme"}}
        
    def authenticate_via_cookie(self, cookie_header, sec_fetch_site, csrf_token_header, expected_csrf_token):
        """
        Cookie-Based Authentication:
        Browser attaches cookies automatically on every request to the domain.
        - XSS Protection: HttpOnly flag prevents JavaScript from accessing document.cookie.
        - CSRF Vulnerability: If a victim visits evil.com, evil.com can submit a form to bank.com
          and the browser will attach the session cookie automatically!
        - CSRF Defense: SameSite=Lax/Strict cookie attribute + double-submit Anti-CSRF token header.
        """
        session_id = cookie_header.get("session_id")
        if not session_id or session_id not in self.sessions:
            return 401, "Invalid session"

        # CSRF Defense Check:
        if sec_fetch_site == "cross-site":
            if csrf_token_header != expected_csrf_token:
                return 403, "CSRF attack detected: cross-site request missing valid Anti-CSRF header"

        return 200, self.sessions[session_id]

    def authenticate_via_bearer_token(self, auth_header):
        """
        Bearer Token Authentication (JWT in Authorization header):
        - CSRF Immune: Browsers NEVER attach Authorization headers automatically to cross-site requests.
        - XSS Vulnerable: If frontend stores the token in localStorage, any XSS vulnerability
          allows attackers to steal the token and impersonate the user indefinitely.
        """
        if not auth_header or not auth_header.startswith("Bearer "):
            return 401, "Missing bearer token"
            
        token = auth_header.split(" ", 1)[1]
        if token == "jwt_secret_token":
            return 200, {"user_id": "usr_alice", "tenant": "acme"}
        return 401, "Invalid token"

sec = SecurityContextSimulator()

# 1. Cookie authentication with CSRF attack:
# Attacker site triggers cross-site POST with victim's auto-attached session cookie:
cookie_header = {"session_id": "sess_cookie_123"}
status_csrf, msg_csrf = sec.authenticate_via_cookie(
    cookie_header, sec_fetch_site="cross-site", csrf_token_header=None, expected_csrf_token="anti_csrf_token_99"
)
assert status_csrf == 403, "CSRF attack successfully blocked by Anti-CSRF validation"

# 2. Bearer token immunity to CSRF:
status_bearer, user = sec.authenticate_via_bearer_token("Bearer jwt_secret_token")
assert status_bearer == 200 and user["user_id"] == "usr_alice"

print(f"Auth trust boundaries verified: cookie_csrf_blocked={status_csrf}, bearer_authenticated={status_bearer}")

