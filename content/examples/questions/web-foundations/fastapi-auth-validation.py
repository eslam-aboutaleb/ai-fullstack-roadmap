"""Demonstrate FastAPI-style ASGI request parsing, Pydantic validation, and dependency-injected authorization."""
import json

class ValidationError(Exception):
    def __init__(self, errors):
        self.errors = errors

class UserModel:
    """Simulate Pydantic schema validation."""
    def __init__(self, data):
        errors = []
        if not isinstance(data.get("email"), str) or "@" not in data.get("email", ""):
            errors.append({"field": "email", "msg": "Invalid email address"})
        
        amount = data.get("amount_cents")
        if not isinstance(amount, int) or amount <= 0:
            errors.append({"field": "amount_cents", "msg": "Amount must be a positive integer"})
            
        if errors:
            raise ValidationError(errors)
            
        self.email = data["email"]
        self.amount_cents = amount
        self.currency = data.get("currency", "USD")

def authenticate_and_authorize(headers, required_tenant="tenant_acme"):
    """Simulate FastAPI Depends(get_current_user) dependency."""
    auth_header = headers.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        return {"status": 401, "error": "Missing or malformed Authorization header"}
        
    token = auth_header.split(" ", 1)[1]
    # Simulated JWT payload
    if token == "token_alice_acme":
        user_tenant = "tenant_acme"
        user_id = "usr_alice"
    elif token == "token_bob_other":
        user_tenant = "tenant_other"
        user_id = "usr_bob"
    else:
        return {"status": 401, "error": "Invalid or expired token"}

    if user_tenant != required_tenant:
        return {"status": 403, "error": "Forbidden: User does not belong to target tenant organization"}

    return {"status": 200, "user_id": user_id, "tenant": user_tenant}

def handle_create_invoice_endpoint(headers, raw_body_bytes):
    # Step 1: Authentication & Authorization Dependency Check
    auth_result = authenticate_and_authorize(headers, required_tenant="tenant_acme")
    if auth_result["status"] != 200:
        return auth_result["status"], {"error": auth_result["error"]}

    # Step 2: Request Body Parsing & Schema Validation
    try:
        payload = json.loads(raw_body_bytes.decode("utf-8"))
        validated_data = UserModel(payload)
    except json.JSONDecodeError:
        return 400, {"error": "Malformed JSON payload"}
    except ValidationError as ve:
        return 422, {"detail": ve.errors} # Standard FastAPI 422 Unprocessable Entity

    # Step 3: Business Logic
    return 201, {
        "invoice_id": "inv_101",
        "email": validated_data.email,
        "amount": validated_data.amount_cents,
        "created_by": auth_result["user_id"]
    }

# Test 1: Valid authorized request -> 201 Created
status1, body1 = handle_create_invoice_endpoint(
    {"authorization": "Bearer token_alice_acme"},
    b'{"email": "alice@acme.corp", "amount_cents": 5000}'
)
assert status1 == 201 and body1["invoice_id"] == "inv_101"

# Test 2: Validation failure (negative amount) -> 422 Unprocessable Entity
status2, body2 = handle_create_invoice_endpoint(
    {"authorization": "Bearer token_alice_acme"},
    b'{"email": "alice@acme.corp", "amount_cents": -500}'
)
assert status2 == 422 and body2["detail"][0]["field"] == "amount_cents"

# Test 3: Cross-tenant authorization denial -> 403 Forbidden
status3, body3 = handle_create_invoice_endpoint(
    {"authorization": "Bearer token_bob_other"},
    b'{"email": "bob@other.corp", "amount_cents": 5000}'
)
assert status3 == 403

print(f"FastAPI validation & auth verified: valid={status1}, invalid_schema={status2}, cross_tenant={status3}")

