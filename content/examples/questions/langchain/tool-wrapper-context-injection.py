"""LangChain Tool Wrapper, ContextVar Identity Injection, and Domain Perimeter Security.

Demonstrates:
1. Tool Wrapper Adaptation:
   - Adapts an existing domain service method into an LLM-callable tool with validated Pydantic arguments.
2. ContextVar Identity Injection:
   - Injects trusted authenticated caller identity (tenant_id, user_id) directly from request-local ContextVar.
   - Strictly omits security/identity fields from the model-facing schema to eliminate model-injected IDOR attacks.
3. Authority Invariant:
   - Business authorization checks remain inside the domain service, not duplicated in the wrapper.
"""

from contextvars import ContextVar
from dataclasses import dataclass
import inspect
import json
from typing import Any, Callable, Dict, List, Optional


# Request-local context holding authenticated principal
CURRENT_TENANT_ID: ContextVar[Optional[str]] = ContextVar("current_tenant_id", default=None)
CURRENT_USER_ID: ContextVar[Optional[str]] = ContextVar("current_user_id", default=None)


class DomainOrderService:
    """Core enterprise business service enforcing tenant isolation and business rules."""

    DATABASE = {
        ("tenant_alpha", "ORD-101"): {"customer": "Alice", "total": 150.00, "status": "SHIPPED"},
        ("tenant_alpha", "ORD-102"): {"customer": "Bob", "total": 85.50, "status": "PENDING"},
        ("tenant_beta", "ORD-999"): {"customer": "SecretCorp", "total": 9999.00, "status": "CONFIDENTIAL"},
    }

    @classmethod
    def get_order_details(cls, tenant_id: str, order_id: str) -> Dict[str, Any]:
        """Business method strictly requiring validated tenant_id."""
        if not tenant_id:
            raise PermissionError("Access Denied: Missing tenant identity")

        key = (tenant_id, order_id.upper().strip())
        record = cls.DATABASE.get(key)
        if not record:
            raise KeyError(f"Order '{order_id}' not found for tenant '{tenant_id}'")

        return {"order_id": order_id, "tenant": tenant_id, "data": record}


class LangChainToolWrapper:
    """Simulates LangChain @tool decorator with automatic ContextVar injection."""

    def __init__(self, name: str, description: str, func: Callable, exposed_params: List[str]):
        self.name = name
        self.description = description
        self.func = func
        self.exposed_params = exposed_params

    def get_model_schema(self) -> Dict[str, Any]:
        """Generates model-facing JSON Schema exposing ONLY safe user arguments."""
        properties = {}
        for p in self.exposed_params:
            properties[p] = {"type": "string", "description": f"The {p} parameter"}

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": self.exposed_params
                }
            }
        }

    def invoke(self, model_arguments: Dict[str, Any]) -> str:
        """Invokes domain service injecting trusted context parameters outside model control."""
        tenant_id = CURRENT_TENANT_ID.get()
        if not tenant_id:
            return json.dumps({"error": "Unauthenticated: No active tenant context in request"})

        try:
            # Model arguments only provide order_id! tenant_id is injected from server context!
            order_id = model_arguments.get("order_id", "")
            result = self.func(tenant_id=tenant_id, order_id=order_id)
            return json.dumps({"success": True, "result": result})
        except Exception as err:
            return json.dumps({"success": False, "error": str(err)})


def create_order_tool() -> LangChainToolWrapper:
    return LangChainToolWrapper(
        name="lookup_order",
        description="Lookup customer order details by order_id.",
        func=DomainOrderService.get_order_details,
        exposed_params=["order_id"]  # Notice: tenant_id is NOT exposed to the model!
    )


def main():
    order_tool = create_order_tool()

    # 1. Inspect Model Schema
    print("1. Model-Facing Tool Schema Inspection:")
    schema = order_tool.get_model_schema()
    print(json.dumps(schema, indent=2))

    # Assert that tenant_id is completely omitted from model-facing schema
    assert "tenant_id" not in schema["function"]["parameters"]["properties"]
    assert "order_id" in schema["function"]["parameters"]["properties"]

    # 2. Test Authorized Invocation within Tenant Alpha Context
    print("\n2. Authorized Invocation for Tenant Alpha:")
    token_tenant = CURRENT_TENANT_ID.set("tenant_alpha")
    token_user = CURRENT_USER_ID.set("user_alice_42")

    try:
        raw_res = order_tool.invoke({"order_id": "ORD-101"})
        res = json.loads(raw_res)
        print(f"  Result: {res}")
        assert res["success"] is True
        assert res["result"]["data"]["customer"] == "Alice"

        # 3. Test Cross-Tenant Data Tampering (IDOR Attempt)
        print("\n3. Testing Cross-Tenant Access Protection (Tenant Beta Order):")
        # Attacker tries to query an order belonging to tenant_beta while in tenant_alpha context
        idor_res_raw = order_tool.invoke({"order_id": "ORD-999"})
        idor_res = json.loads(idor_res_raw)
        print(f"  IDOR Result: {idor_res}")
        assert idor_res["success"] is False
        assert "not found for tenant 'tenant_alpha'" in idor_res["error"]

    finally:
        CURRENT_TENANT_ID.reset(token_tenant)
        CURRENT_USER_ID.reset(token_user)

    # 4. Test Unauthenticated Invocation
    print("\n4. Testing Unauthenticated Request Context:")
    unauth_res = json.loads(order_tool.invoke({"order_id": "ORD-101"}))
    print(f"  Unauth Result: {unauth_res}")
    assert "Unauthenticated" in unauth_res["error"]

    print("\nTool wrapper, ContextVar identity injection, and domain authorization verified successfully.")


if __name__ == "__main__":
    main()
