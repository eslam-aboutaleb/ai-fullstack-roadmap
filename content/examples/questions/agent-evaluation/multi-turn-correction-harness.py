# /// script
# dependencies = []
# ///
"""
Multi-Turn Conversational Request Preparation and Correction Testing Harness.

Tests how an agent handles interactive multi-turn dialogues:
1. Context preservation across turns (retains valid parameters when updating another).
2. Approval gating: altering an approved item invalidates prior approvals.
3. Re-prompting for user authorization when core mutation parameters change.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ConversationState:
    item_id: Optional[str] = None
    item_price: float = 0.0
    user_approved_item: Optional[str] = None
    is_authorized: bool = False
    status: str = "AWAITING_INPUT"


class InteractivePurchaseAgent:
    """Agent managing multi-turn purchase preparation with authorization gates."""

    def __init__(self) -> None:
        self.catalog = {
            "item_budget_a": {"name": "Standard Laptop", "price": 800.0},
            "item_luxury_b": {"name": "Enterprise Workstation", "price": 3200.0},
        }
        self.state = ConversationState()

    def handle_turn(self, user_intent: str, item_id: Optional[str] = None, user_confirmed: bool = False) -> str:
        # If user specifies or changes item
        if item_id:
            if item_id not in self.catalog:
                return "Item not found in catalog."

            # If user corrects or changes item, invalidate any prior approval
            if self.state.item_id and self.state.item_id != item_id:
                self.state.user_approved_item = None
                self.state.is_authorized = False

            self.state.item_id = item_id
            self.state.item_price = self.catalog[item_id]["price"]
            self.state.status = "PENDING_CONFIRMATION"

        # Check confirmation
        if user_confirmed:
            if self.state.item_id:
                self.state.user_approved_item = self.state.item_id
                self.state.is_authorized = True
                self.state.status = "AUTHORIZED"
                return f"Approved purchase of {self.state.item_id} (${self.state.item_price}). Ready to execute."

        if self.state.status == "PENDING_CONFIRMATION":
            return f"Selected {self.state.item_id} for ${self.state.item_price}. Please confirm purchase."

        return "How can I help you today?"

    def execute_purchase(self) -> Dict[str, Any]:
        """Mutation gate: ensures current item strictly matches the approved item."""
        if not self.state.is_authorized:
            raise PermissionError("Action denied: purchase was not authorized by user.")

        if self.state.item_id != self.state.user_approved_item:
            raise PermissionError(
                f"Action denied: Current item '{self.state.item_id}' does not match approved item '{self.state.user_approved_item}'!"
            )

        self.state.status = "COMMITTED"
        return {"result": "ORDER_PLACED", "item_id": self.state.item_id, "amount": self.state.item_price}


def main() -> None:
    agent = InteractivePurchaseAgent()

    # --- Turn 1: User selects Item A and confirms approval ---
    agent.handle_turn(user_intent="select_item", item_id="item_budget_a", user_confirmed=False)
    agent.handle_turn(user_intent="confirm_purchase", user_confirmed=True)
    assert agent.state.item_id == "item_budget_a"
    assert agent.state.user_approved_item == "item_budget_a"
    assert agent.state.is_authorized is True

    # --- Turn 2: User issues a correction changing item to Item B ---
    # The agent must update item_id to Item B, BUT invalidate previous approval!
    agent.handle_turn(user_intent="correct_item", item_id="item_luxury_b", user_confirmed=False)
    assert agent.state.item_id == "item_luxury_b"
    assert agent.state.item_price == 3200.0
    state_updated = True

    # Critical Security Check: Attempting to execute mutation now MUST fail!
    assert agent.state.is_authorized is False, "Prior approval must be invalidated upon correction"
    assert agent.state.user_approved_item is None
    prior_approval_invalidated = True

    try:
        agent.execute_purchase()
        raise AssertionError("Should have raised PermissionError for unauthorized modified item!")
    except PermissionError:
        pass  # Expected protection

    # --- Turn 3: User explicitly re-confirms Item B ---
    msg = agent.handle_turn(user_intent="confirm_purchase", user_confirmed=True)
    assert "Approved purchase of item_luxury_b" in msg
    assert agent.state.is_authorized is True
    assert agent.state.user_approved_item == "item_luxury_b"

    order_result = agent.execute_purchase()
    assert order_result["result"] == "ORDER_PLACED"
    assert order_result["item_id"] == "item_luxury_b"
    final_reapproval_committed = True

    print(
        f"Multi-turn correction harness verified: state_updated={state_updated}, "
        f"prior_approval_invalidated={prior_approval_invalidated}, "
        f"final_reapproval_committed={final_reapproval_committed}"
    )


if __name__ == "__main__":
    main()

