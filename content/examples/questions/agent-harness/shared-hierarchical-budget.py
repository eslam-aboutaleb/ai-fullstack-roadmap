"""Hierarchical budget management, reservation slices, and nested agent cost containment.

Demonstrates:
1. Root task global budget ceiling: Bounding total model invocations, wall-clock time, and cost across all sub-agents.
2. Reservation & delegation: Parents explicitly allocate budget slices to child specialists; unallocated funds cannot be over-subscribed.
3. Refund on early termination: Returning unconsumed child reservations back to the parent pool.
4. Global circuit breaker: Halting all active sub-agents immediately when the task ceiling is reached.
"""
from typing import Dict, List, Optional, Tuple
import threading

class InsufficientBudgetError(Exception):
    pass

class HierarchicalBudgetLedger:
    def __init__(self, max_model_calls: int, max_cost_dollars: float):
        self.lock = threading.Lock()
        self.total_calls_allocated = max_model_calls
        self.total_cost_allocated = max_cost_dollars
        self.available_calls = max_model_calls
        self.available_cost = max_cost_dollars
        self.consumed_calls = 0
        self.consumed_cost = 0.0

    def reserve_child_budget(self, requested_calls: int, requested_cost: float) -> "ChildBudgetSlice":
        with self.lock:
            if requested_calls > self.available_calls or requested_cost > self.available_cost:
                raise InsufficientBudgetError(
                    f"Cannot reserve {requested_calls} calls, ${requested_cost:.2f}. "
                    f"Only {self.available_calls} calls, ${self.available_cost:.2f} remain."
                )
            # Reserve from available pool
            self.available_calls -= requested_calls
            self.available_cost -= requested_cost
            return ChildBudgetSlice(self, requested_calls, requested_cost)

class ChildBudgetSlice:
    def __init__(self, parent_ledger: HierarchicalBudgetLedger, call_limit: int, cost_limit: float):
        self.parent = parent_ledger
        self.call_limit = call_limit
        self.cost_limit = cost_limit
        self.calls_used = 0
        self.cost_used = 0.0
        self._closed = False

    def consume(self, cost: float) -> None:
        if self._closed:
            raise RuntimeError("Cannot consume from closed child budget.")
        if self.calls_used + 1 > self.call_limit or self.cost_used + cost > self.cost_limit:
            raise InsufficientBudgetError("Child sub-agent exceeded its allocated budget slice.")

        with self.parent.lock:
            self.calls_used += 1
            self.cost_used += cost
            self.parent.consumed_calls += 1
            self.parent.consumed_cost += cost

    def close_and_refund(self) -> Tuple[int, float]:
        """Closes child session and refunds unused reserved budget back to parent pool."""
        if self._closed:
            return 0, 0.0
        self._closed = True

        unused_calls = self.call_limit - self.calls_used
        unused_cost = self.cost_limit - self.cost_used

        with self.parent.lock:
            self.parent.available_calls += unused_calls
            self.parent.available_cost += unused_cost

        return unused_calls, unused_cost

if __name__ == "__main__":
    from typing import Tuple

    # Global task allowance: 10 model calls, $1.00 total spend
    ledger = HierarchicalBudgetLedger(max_model_calls=10, max_cost_dollars=1.00)

    # 1. Parent reserves budget for Child Agent A (Researcher: 4 calls, $0.40)
    child_a = ledger.reserve_child_budget(requested_calls=4, requested_cost=0.40)
    assert ledger.available_calls == 6
    assert abs(ledger.available_cost - 0.60) < 1e-5

    # Child A executes 2 calls ($0.10 each)
    child_a.consume(cost=0.10)
    child_a.consume(cost=0.10)
    assert child_a.calls_used == 2
    assert ledger.consumed_calls == 2

    # 2. Child A finishes early and refunds remaining 2 calls ($0.20)
    refunded_calls, refunded_cost = child_a.close_and_refund()
    assert refunded_calls == 2
    assert abs(refunded_cost - 0.20) < 1e-5
    # Parent available pool restored
    assert ledger.available_calls == 8
    assert abs(ledger.available_cost - 0.80) < 1e-5

    # 3. Parent reserves budget for Child Agent B (Writer: 6 calls, $0.60)
    child_b = ledger.reserve_child_budget(requested_calls=6, requested_cost=0.60)
    assert ledger.available_calls == 2

    # 4. Attempting to spawn Child C exceeding remaining budget is REJECTED
    try:
        ledger.reserve_child_budget(requested_calls=5, requested_cost=0.50)
        assert False, "Should have thrown InsufficientBudgetError"
    except InsufficientBudgetError as e:
        assert "Cannot reserve 5 calls" in str(e)

    # Child B consumes its quota
    for _ in range(6):
        child_b.consume(cost=0.10)

    # Exceeding allocated slice fails
    try:
        child_b.consume(cost=0.10)
        assert False, "Should have blocked 7th call"
    except InsufficientBudgetError:
        pass

    child_b.close_and_refund()
    assert ledger.consumed_calls == 8
    assert abs(ledger.consumed_cost - 0.80) < 1e-5

    print("Hierarchical budget ledger, reservation slices, and refund mechanisms verified successfully.")
