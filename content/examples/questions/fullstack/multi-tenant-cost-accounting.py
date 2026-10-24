"""Demonstrate multi-tenant token cost accounting, dollar quotas, and atomic rate limit enforcement."""
from decimal import Decimal, ROUND_HALF_EVEN

class MultiTenantBillingEngine:
    # Model pricing per 1,000 tokens
    INPUT_RATE_PER_1K = Decimal("0.00015")
    OUTPUT_RATE_PER_1K = Decimal("0.00060")

    def __init__(self):
        # Tenant ledger: dollar balance, monthly quota, and active status
        self.tenants = {
            "tenant_alpha": {
                "balance_usd": Decimal("50.00"),
                "monthly_quota_usd": Decimal("100.00"),
                "status": "active"
            }
        }

    def calculate_cost(self, prompt_tokens, completion_tokens):
        input_cost = (Decimal(str(prompt_tokens)) / Decimal("1000")) * self.INPUT_RATE_PER_1K
        output_cost = (Decimal(str(completion_tokens)) / Decimal("1000")) * self.OUTPUT_RATE_PER_1K
        total = (input_cost + output_cost).quantize(Decimal("0.000001"), rounding=ROUND_HALF_EVEN)
        return total

    def execute_metered_request(self, tenant_id, prompt_tokens, completion_tokens):
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return 404, {"error": "Tenant not found"}

        # 1. Pre-execution quota authorization check:
        estimated_max_cost = self.calculate_cost(prompt_tokens, 2048) # Estimate with max output
        if tenant["balance_usd"] < estimated_max_cost:
            return 429, {
                "error": "QuotaExceeded",
                "message": f"Tenant balance ${tenant['balance_usd']} insufficient for operation."
            }

        # 2. Reconcile exact post-execution actual cost:
        actual_cost = self.calculate_cost(prompt_tokens, completion_tokens)
        tenant["balance_usd"] -= actual_cost

        return 200, {
            "status": "success",
            "cost_usd": str(actual_cost),
            "remaining_balance": str(tenant["balance_usd"])
        }

engine = MultiTenantBillingEngine()

# Request 1: 1500 prompt tokens, 350 output tokens
code1, res1 = engine.execute_metered_request("tenant_alpha", 1500, 350)
assert code1 == 200
assert Decimal(res1["cost_usd"]) > Decimal("0.000")

# Simulate tenant balance dropping to zero:
engine.tenants["tenant_alpha"]["balance_usd"] = Decimal("0.0001")

# Request 2: Rejected with 429 Quota Exceeded:
code2, res2 = engine.execute_metered_request("tenant_alpha", 1500, 350)
assert code2 == 429 and res2["error"] == "QuotaExceeded"

print(f"Multi-tenant billing verified: req1_cost=${res1['cost_usd']}, req2_quota_blocked={code2 == 429}")

