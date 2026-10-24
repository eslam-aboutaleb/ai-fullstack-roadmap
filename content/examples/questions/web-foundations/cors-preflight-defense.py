"""Demonstrate CORS preflight OPTIONS negotiation and browser security boundaries."""

class CORSServerSimulator:
    def __init__(self, allowed_origins):
        self.allowed_origins = set(allowed_origins)

    def handle_preflight_options(self, origin, request_method, request_headers):
        """
        Browser Preflight: Browser sends OPTIONS before non-simple cross-origin requests
        (e.g. POST with Authorization header or application/json content-type).
        """
        response_headers = {}
        
        # Check Origin allowlist:
        if origin in self.allowed_origins:
            response_headers["Access-Control-Allow-Origin"] = origin
            response_headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response_headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, Idempotency-Key"
            response_headers["Access-Control-Max-Age"] = "86400" # Cache preflight for 24 hours
            response_headers["Access-Control-Allow-Credentials"] = "true"
            return 204, response_headers
        else:
            # Origin not allowed: omit Access-Control-Allow-Origin; browser blocks the frontend JavaScript
            return 403, response_headers

    def handle_api_request(self, origin, is_browser_client, auth_token):
        """
        CRITICAL LESSON: CORS is a BROWSER policy, NOT a server firewall.
        Non-browser clients (curl, backend microservices, malicious Python scripts)
        DO NOT enforce CORS and can bypass Origin restrictions completely.
        Therefore, server-side authentication (Bearer token) is ALWAYS required.
        """
        # If client is a browser and origin is untrusted:
        if is_browser_client and origin not in self.allowed_origins:
            return 403, "Blocked by Browser CORS Policy"
            
        # For all requests, server enforces authentication:
        if auth_token != "valid_token":
            return 401, "Unauthorized"

        return 200, "Secure Resource Accessed"

cors_server = CORSServerSimulator(allowed_origins=["https://dashboard.example.com"])

# 1. Trusted browser origin preflight -> 204 with CORS allow headers:
status_opt, headers_opt = cors_server.handle_preflight_options(
    "https://dashboard.example.com", "POST", "Authorization, Content-Type"
)
assert status_opt == 204
assert headers_opt["Access-Control-Allow-Origin"] == "https://dashboard.example.com"

# 2. Untrusted browser origin (e.g. malicious site) -> 403 / blocked by browser:
status_bad, _ = cors_server.handle_preflight_options("https://evil-site.com", "POST", "Authorization")
assert status_bad == 403

# 3. Direct curl / script without browser sandbox (proves CORS != server firewall):
status_curl, body_curl = cors_server.handle_api_request(
    origin="https://evil-site.com", is_browser_client=False, auth_token="valid_token"
)
assert status_curl == 200, "Non-browser clients ignore CORS; server auth protected the endpoint"

print(f"CORS security boundary verified: preflight_allowed={status_opt}, preflight_blocked={status_bad}, curl_bypass_handled={status_curl}")

