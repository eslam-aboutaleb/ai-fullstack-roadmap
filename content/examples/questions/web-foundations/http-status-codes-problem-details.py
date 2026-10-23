"""Implement RFC 7807 / RFC 9457 Problem Details error contract across HTTP status codes."""

def create_problem_details(status_code, title, detail, error_type, instance_uri, invalid_params=None):
    """
    RFC 9457 Problem Details for HTTP APIs standard representation.
    Provides machine-readable error categories instead of raw 200 OK with error strings.
    """
    problem = {
        "type": f"https://api.example.com/errors/{error_type}",
        "title": title,
        "status": status_code,
        "detail": detail,
        "instance": instance_uri
    }
    if invalid_params:
        problem["invalid_params"] = invalid_params
    return problem

def dispatch_api_request(endpoint, auth_token, user_role, body):
    # 1. 401 Unauthorized: Missing or invalid authentication credential
    if not auth_token:
        return 401, create_problem_details(
            401, "Unauthorized", "No authentication token provided in Authorization header.",
            "unauthorized", endpoint
        )

    # 2. 403 Forbidden: Authenticated user lacks permission
    if user_role != "admin" and "admin" in endpoint:
        return 403, create_problem_details(
            403, "Forbidden", "User lacks admin role required for this administrative resource.",
            "insufficient-permissions", endpoint
        )

    # 3. 422 Unprocessable Content: Syntactically valid JSON failing semantic business constraints
    if body and body.get("temperature", 0) > 2.0:
        return 422, create_problem_details(
            422, "Unprocessable Entity", "Model parameter temperature exceeds maximum allowed value.",
            "validation-error", endpoint,
            invalid_params=[{"name": "temperature", "reason": "Must be <= 2.0"}]
        )

    # 4. 404 Not Found: Target resource does not exist
    if endpoint == "/api/documents/non_existent":
        return 404, create_problem_details(
            404, "Not Found", "Document ID 'non_existent' could not be found.",
            "resource-not-found", endpoint
        )

    # 200 OK
    return 200, {"status": "success"}

# Verify distinct error classes:
code_401, prob_401 = dispatch_api_request("/api/models", None, "user", {})
assert code_401 == 401 and prob_401["title"] == "Unauthorized"

code_403, prob_403 = dispatch_api_request("/api/admin/metrics", "valid_token", "user", {})
assert code_403 == 403 and prob_403["title"] == "Forbidden"

code_422, prob_422 = dispatch_api_request("/api/generate", "valid_token", "user", {"temperature": 5.0})
assert code_422 == 422 and prob_422["invalid_params"][0]["name"] == "temperature"

print(f"Problem details contract verified: 401={code_401}, 403={code_403}, 422={code_422}")
