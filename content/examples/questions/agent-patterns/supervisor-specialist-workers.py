"""Supervisor-Specialist Worker Pattern with Strict Capability and Permission Boundaries.

Demonstrates:
1. Operational justification for specialists: capability differences, least-privilege security boundaries,
   and context efficiency (preventing tool schema dilution).
2. Isolated Tool Registries:
   - ResearchWorker: read-only documentation tools; zero access to internal financial ledgers.
   - FinancialAccountWorker: restricted ledger tools requiring authentication token; zero internet access.
3. Supervisor Coordinator: assigns bounded typed subtasks, validates worker contracts, and aggregates
   typed outputs without leaking coordinator authority to sub-workers.
"""

from dataclasses import dataclass, field
import json
from typing import Any, Dict, List, Optional, Set


@dataclass
class WorkerTask:
    task_type: str
    payload: Dict[str, Any]
    requester_token: str


@dataclass
class WorkerResult:
    worker_id: str
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None


class BaseWorker:
    def __init__(self, worker_id: str, allowed_capabilities: Set[str]):
        self.worker_id = worker_id
        self.allowed_capabilities = allowed_capabilities

    def validate_capability(self, capability: str):
        if capability not in self.allowed_capabilities:
            raise PermissionError(
                f"Worker '{self.worker_id}' denied access to capability '{capability}'. "
                f"Allowed: {sorted(self.allowed_capabilities)}"
            )


class ResearchSpecialist(BaseWorker):
    """Read-only research specialist. Has access to policy docs, no financial ledger access."""

    def __init__(self):
        super().__init__("research_specialist", allowed_capabilities={"search_policy", "fetch_glossary"})
        self.knowledge = {
            "tier_gold": "Gold tier members receive 30 days return window and free return shipping.",
            "tier_silver": "Silver tier members receive 14 days return window and standard shipping."
        }

    def execute(self, task: WorkerTask) -> WorkerResult:
        try:
            self.validate_capability(task.task_type)
            if task.task_type == "search_policy":
                tier = task.payload.get("customer_tier", "tier_silver")
                policy = self.knowledge.get(tier, "Default: 7 days return window.")
                return WorkerResult(worker_id=self.worker_id, success=True, data={"policy_terms": policy})
            raise NotImplementedError(f"Task type {task.task_type}")
        except Exception as err:
            return WorkerResult(worker_id=self.worker_id, success=False, data={}, error=str(err))


class FinancialLedgerSpecialist(BaseWorker):
    """Financial account specialist. Requires authenticated JWT token and has ledger access."""

    def __init__(self):
        super().__init__("financial_specialist", allowed_capabilities={"check_balance", "calculate_refund"})
        self.accounts = {
            "ACCT-100": {"balance": 450.0, "status": "active", "tier": "tier_gold"},
            "ACCT-200": {"balance": 15.0, "status": "active", "tier": "tier_silver"}
        }

    def execute(self, task: WorkerTask) -> WorkerResult:
        try:
            # Enforce authentication token
            if not task.requester_token or not task.requester_token.startswith("auth_"):
                raise PermissionError("Unauthenticated request: valid bearer token required for ledger access")

            self.validate_capability(task.task_type)

            if task.task_type == "calculate_refund":
                account_id = task.payload["account_id"]
                item_price = task.payload["item_price"]
                acct = self.accounts.get(account_id)
                if not acct:
                    raise KeyError(f"Account {account_id} not found")

                # Gold gets free shipping deduction (0), silver gets 10 shipping fee deducted
                shipping_deduction = 0.0 if acct["tier"] == "tier_gold" else 10.0
                net_refund = max(0.0, item_price - shipping_deduction)
                return WorkerResult(
                    worker_id=self.worker_id,
                    success=True,
                    data={"account_id": account_id, "tier": acct["tier"], "net_refund": net_refund}
                )
            raise NotImplementedError(f"Task type {task.task_type}")
        except Exception as err:
            return WorkerResult(worker_id=self.worker_id, success=False, data={}, error=str(err))


class SupervisorAgent:
    """Supervisor orchestrating specialist workers and aggregating their typed contracts."""

    def __init__(self, research_worker: ResearchSpecialist, ledger_worker: FinancialLedgerSpecialist):
        self.research_worker = research_worker
        self.ledger_worker = ledger_worker

    def process_customer_return_request(self, account_id: str, item_price: float, supervisor_token: str) -> Dict[str, Any]:
        # Step 1: Delegate financial calculation to ledger specialist
        ledger_task = WorkerTask(
            task_type="calculate_refund",
            payload={"account_id": account_id, "item_price": item_price},
            requester_token=supervisor_token
        )
        ledger_res = self.ledger_worker.execute(ledger_task)
        if not ledger_res.success:
            return {"status": "FAILED", "stage": "ledger", "error": ledger_res.error}

        tier = ledger_res.data["tier"]
        net_refund = ledger_res.data["net_refund"]

        # Step 2: Delegate policy terms lookup to research specialist
        research_task = WorkerTask(
            task_type="search_policy",
            payload={"customer_tier": tier},
            requester_token=supervisor_token
        )
        research_res = self.research_worker.execute(research_task)
        if not research_res.success:
            return {"status": "FAILED", "stage": "research", "error": research_res.error}

        # Step 3: Combine typed outputs into cohesive customer response
        policy_terms = research_res.data["policy_terms"]
        return {
            "status": "SUCCESS",
            "account_id": account_id,
            "tier": tier,
            "net_refund": net_refund,
            "policy": policy_terms,
            "summary": f"Approved refund of ${net_refund:.2f} under {tier} terms ({policy_terms})"
        }


def main():
    researcher = ResearchSpecialist()
    ledger = FinancialLedgerSpecialist()
    supervisor = SupervisorAgent(researcher, ledger)

    # 1. Test Security Isolation: researcher cannot be given ledger capability
    malicious_task = WorkerTask(
        task_type="calculate_refund",
        payload={"account_id": "ACCT-100", "item_price": 50.0},
        requester_token="auth_supervisor_token"
    )
    res = researcher.execute(malicious_task)
    print("Testing Capability Isolation:")
    print(f"  Researcher rejected ledger action: {not res.success} (Error: {res.error})")
    assert not res.success
    assert "denied access" in res.error

    # 2. Test Ledger Authentication Enforcement
    unauth_task = WorkerTask(
        task_type="calculate_refund",
        payload={"account_id": "ACCT-100", "item_price": 50.0},
        requester_token="invalid_token"
    )
    unauth_res = ledger.execute(unauth_task)
    print(f"  Ledger rejected invalid token: {not unauth_res.success} (Error: {unauth_res.error})")
    assert not unauth_res.success
    assert "Unauthenticated" in unauth_res.error

    # 3. Test Successful Supervisor Aggregation
    result = supervisor.process_customer_return_request(
        account_id="ACCT-100",
        item_price=120.0,
        supervisor_token="auth_valid_supervisor"
    )
    print("\nSupervisor Orchestration Result:")
    print(json.dumps(result, indent=2))

    assert result["status"] == "SUCCESS"
    assert result["tier"] == "tier_gold"
    assert result["net_refund"] == 120.0  # Gold gets free shipping
    assert "Gold tier members receive 30 days" in result["policy"]

    print("\nSupervisor-specialist worker pattern with typed contracts verified.")


if __name__ == "__main__":
    main()

