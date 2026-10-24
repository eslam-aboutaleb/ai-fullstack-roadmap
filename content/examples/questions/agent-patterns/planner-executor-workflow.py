"""Planner-Executor Pattern with Pre-flight Policy Validation and Dynamic Re-planning.

Demonstrates:
1. Separation of concerns: Planner (high-level LLM reasoning) outputs structured DAG plan;
   Executor (deterministic runtime) validates, schedules, and executes tasks.
2. Pre-flight Policy Inspection: Host inspects the proposed plan BEFORE any side-effect occurs;
   blocks unauthorized actions (e.g., direct financial mutations without approval token).
3. Dependency-aware execution: runs independent tasks concurrently and dependent tasks in order.
4. Dynamic re-planning: when an observation invalidates assumptions (e.g., out-of-stock),
   execution pauses and the planner produces an alternate recovery plan.
"""

from dataclasses import dataclass, field
from enum import Enum
import json
from typing import Any, Dict, List, Optional, Set, Tuple


class TaskStatus(Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


@dataclass
class PlanTask:
    task_id: str
    action: str
    params: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)
    requires_admin: bool = False
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Any] = None


@dataclass
class ExecutionPlan:
    goal: str
    tasks: List[PlanTask]

    def get_task(self, task_id: str) -> Optional[PlanTask]:
        for t in self.tasks:
            if t.task_id == task_id:
                return t
        return None


class PolicyValidator:
    """Pre-flight security and safety gate inspecting plans before execution."""

    ALLOWED_ACTIONS = {"check_inventory", "reserve_warehouse_slot", "prepare_refund_draft", "notify_customer"}
    RESTRICTED_ACTIONS = {"execute_wire_transfer", "delete_customer_record"}

    @classmethod
    def validate_plan(cls, plan: ExecutionPlan, user_roles: Set[str]) -> Tuple[bool, Optional[str]]:
        for task in plan.tasks:
            if task.action in cls.RESTRICTED_ACTIONS:
                if "admin" not in user_roles:
                    return False, f"Policy Violation: Action '{task.action}' requires 'admin' role. Found: {user_roles}"

            if task.action not in cls.ALLOWED_ACTIONS and task.action not in cls.RESTRICTED_ACTIONS:
                return False, f"Policy Violation: Action '{task.action}' is not recognized in allowed tool registry"

        return True, None


class MockHostEnvironment:
    """Simulated enterprise environment with inventory and warehouse state."""

    def __init__(self):
        self.inventory = {"SKU-101": 5, "SKU-202": 0}  # SKU-202 is out of stock!
        self.reservations = []
        self.notifications = []

    def execute_tool(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if action == "check_inventory":
            sku = params["sku"]
            qty = self.inventory.get(sku, 0)
            return {"sku": sku, "in_stock": qty > 0, "available_quantity": qty}

        elif action == "reserve_warehouse_slot":
            sku = params["sku"]
            if self.inventory.get(sku, 0) <= 0:
                raise RuntimeError(f"Cannot reserve slot: {sku} is out of stock")
            self.inventory[sku] -= 1
            self.reservations.append(sku)
            return {"sku": sku, "reservation_id": f"RES-{len(self.reservations)}"}

        elif action == "prepare_refund_draft":
            return {"draft_id": f"DRAFT-{params['sku']}", "amount": params.get("amount", 50.0)}

        elif action == "notify_customer":
            msg = params["message"]
            self.notifications.append(msg)
            return {"sent": True, "message": msg}

        raise ValueError(f"Unknown action: {action}")


class PlanExecutor:
    """Deterministic orchestrator executing plan tasks according to dependency order."""

    def __init__(self, host: MockHostEnvironment):
        self.host = host

    def run_plan(self, plan: ExecutionPlan) -> Dict[str, Any]:
        completed_ids = set()

        while True:
            # Find tasks whose dependencies are satisfied and are still PENDING
            runnable = [
                t for t in plan.tasks
                if t.status == TaskStatus.PENDING and all(dep in completed_ids for dep in t.dependencies)
            ]

            if not runnable:
                break

            for task in runnable:
                try:
                    res = self.host.execute_tool(task.action, task.params)
                    task.status = TaskStatus.COMPLETED
                    task.result = res
                    completed_ids.add(task.task_id)
                except Exception as err:
                    task.status = TaskStatus.FAILED
                    task.result = str(err)
                    return {
                        "status": "PAUSED_DISCREPANCY",
                        "failed_task": task.task_id,
                        "error": str(err),
                        "completed_tasks": list(completed_ids)
                    }

        all_completed = all(t.status == TaskStatus.COMPLETED for t in plan.tasks)
        return {
            "status": "COMPLETED" if all_completed else "PARTIALLY_BLOCKED",
            "completed_tasks": list(completed_ids)
        }


def main():
    env = MockHostEnvironment()
    executor = PlanExecutor(env)

    # 1. Test Pre-flight Policy Rejection of Unauthorized Plan
    malicious_plan = ExecutionPlan(
        goal="Process refund via direct wire transfer",
        tasks=[
            PlanTask(task_id="t1", action="check_inventory", params={"sku": "SKU-101"}),
            PlanTask(task_id="t2", action="execute_wire_transfer", params={"amount": 1000}, dependencies=["t1"])
        ]
    )
    valid, err_msg = PolicyValidator.validate_plan(malicious_plan, user_roles={"operator"})
    print("Pre-flight Security Inspection:")
    print(f"  Valid: {valid}, Message: {err_msg}")
    assert valid is False, "Policy validator must reject wire transfer for non-admin user"

    # 2. Test Execution with Out-of-Stock Discrepancy -> Dynamic Re-plan
    initial_plan = ExecutionPlan(
        goal="Order fulfillment for SKU-202 (which is out of stock)",
        tasks=[
            PlanTask(task_id="check_inv", action="check_inventory", params={"sku": "SKU-202"}),
            PlanTask(task_id="reserve_slot", action="reserve_warehouse_slot", params={"sku": "SKU-202"}, dependencies=["check_inv"]),
            PlanTask(task_id="notify", action="notify_customer", params={"message": "Order confirmed!"}, dependencies=["reserve_slot"])
        ]
    )

    valid, _ = PolicyValidator.validate_plan(initial_plan, user_roles={"admin"})
    assert valid is True

    print("\nExecuting Initial Plan:")
    exec_result = executor.run_plan(initial_plan)
    print(f"  Execution result: {exec_result['status']}")
    print(f"  Failed task: {exec_result.get('failed_task')}: {exec_result.get('error')}")
    assert exec_result["status"] == "PAUSED_DISCREPANCY"
    assert exec_result["failed_task"] == "reserve_slot"

    # 3. Dynamic Re-planner Generates Alternate Recovery Plan
    print("\nPlanner generates recovery plan based on failure observation...")
    recovery_plan = ExecutionPlan(
        goal="Alternative recovery: notify out of stock and prepare refund draft",
        tasks=[
            PlanTask(task_id="prep_refund", action="prepare_refund_draft", params={"sku": "SKU-202", "amount": 89.99}),
            PlanTask(task_id="notify_backorder", action="notify_customer", params={"message": "Item SKU-202 out of stock; refund draft prepared."}, dependencies=["prep_refund"])
        ]
    )

    valid, _ = PolicyValidator.validate_plan(recovery_plan, user_roles={"operator"})
    assert valid is True

    recovery_result = executor.run_plan(recovery_plan)
    print(f"  Recovery execution result: {recovery_result['status']}")
    print(f"  Completed tasks: {recovery_result['completed_tasks']}")
    print(f"  Dispatched notifications: {env.notifications}")

    assert recovery_result["status"] == "COMPLETED"
    assert "refund draft prepared" in env.notifications[0]
    print("\nPlanner-Executor pattern with policy gate and recovery verified.")


if __name__ == "__main__":
    main()
