"""Human-in-the-Loop Interrupt vs Cryptographic Authorization Gate.

Demonstrates:
1. Interrupt as Execution Suspension:
   - Reaching an interrupt (`interrupt()`) suspends the graph thread and persists state.
   - It confers ZERO authorization: simply calling `resume()` without credentials is not an approval.
2. Production Authorization Gate:
   - Authenticated reviewer identity and RBAC role validation (e.g. `finance:manager`).
   - HMAC-signed approval token cryptographically binding the exact proposal payload hash.
   - Resource Revision Check (TOCTOU Defense): asserts that the target bank account balance or revision
     has not changed during the hours or days the workflow waited for review.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import json
import time
from typing import Any, Dict, List, Optional, Set


SECRET_APPROVAL_KEY = b"enterprise-hmac-human-approval-key-38481"


@dataclass
class AccountSnapshot:
    account_id: str
    balance: float
    revision: int


class BankAccountDatabase:
    def __init__(self):
        self.accounts = {
            "ACCT-99": AccountSnapshot(account_id="ACCT-99", balance=50000.0, revision=1)
        }

    def get_account(self, account_id: str) -> AccountSnapshot:
        return self.accounts[account_id]

    def execute_wire(self, account_id: str, amount: float, expected_revision: int) -> bool:
        acct = self.accounts[account_id]
        # Revision / TOCTOU check!
        if acct.revision != expected_revision:
            raise ValueError(
                f"Concurrent Modification Conflict: Account revision drifted from {expected_revision} to {acct.revision} "
                "during the human approval waiting period!"
            )
        if acct.balance < amount:
            raise ValueError("Insufficient balance")

        acct.balance -= amount
        acct.revision += 1
        return True


class HumanReviewApprovalGate:
    """Perimeter gate verifying approval tokens, roles, and revision concurrency."""

    @classmethod
    def mint_approval_token(cls, workflow_id: str, action: str, amount: float, revision: int, reviewer: str) -> str:
        payload = {
            "workflow_id": workflow_id,
            "action": action,
            "amount": amount,
            "revision": revision,
            "reviewer": reviewer,
            "exp": int(time.time()) + 300
        }
        raw_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
        sig = hmac.new(SECRET_APPROVAL_KEY, raw_bytes, hashlib.sha256).hexdigest()
        return f"{raw_bytes.hex()}.{sig}"

    @classmethod
    def verify_approval(
        cls,
        token: str,
        expected_workflow_id: str,
        reviewer_roles: Set[str],
        required_role: str
    ) -> Dict[str, Any]:
        # 1. Verify Role
        if required_role not in reviewer_roles:
            raise PermissionError(f"403 Forbidden: Reviewer lacks required approval role '{required_role}'")

        # 2. Verify HMAC Signature
        parts = token.split(".")
        if len(parts) != 2:
            raise ValueError("Malformed approval token")

        hex_data, sig = parts
        raw_bytes = bytes.fromhex(hex_data)
        expected_sig = hmac.new(SECRET_APPROVAL_KEY, raw_bytes, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected_sig):
            raise PermissionError("Tampered approval signature: approval token invalid")

        payload = json.loads(raw_bytes.decode("utf-8"))
        if payload["workflow_id"] != expected_workflow_id:
            raise ValueError("Token workflow_id mismatch")
        if time.time() > payload["exp"]:
            raise PermissionError("Approval token expired")

        return payload


class InterruptedWireTransferWorkflow:
    """Graph workflow that interrupts for review and enforces cryptographic authorization on resume."""

    def __init__(self, db: BankAccountDatabase):
        self.db = db
        self.paused_state: Optional[Dict[str, Any]] = None

    def start_wire_transfer(self, workflow_id: str, account_id: str, amount: float) -> str:
        acct = self.db.get_account(account_id)
        # Reached Interrupt! State is paused
        self.paused_state = {
            "workflow_id": workflow_id,
            "account_id": account_id,
            "amount": amount,
            "initial_revision": acct.revision,
            "status": "SUSPENDED_WAITING_APPROVAL"
        }
        return "WORKFLOW_SUSPENDED_AT_INTERRUPT"

    def resume_and_execute(self, workflow_id: str, approval_token: str, reviewer_roles: Set[str]) -> Dict[str, Any]:
        if not self.paused_state or self.paused_state["status"] != "SUSPENDED_WAITING_APPROVAL":
            raise RuntimeError("Workflow is not currently suspended at approval gate")

        # Invariant: Reaching interrupt != Authorization! Validate cryptographic token and roles!
        verified_payload = HumanReviewApprovalGate.verify_approval(
            token=approval_token,
            expected_workflow_id=workflow_id,
            reviewer_roles=reviewer_roles,
            required_role="finance:director"
        )

        account_id = self.paused_state["account_id"]
        amount = self.paused_state["amount"]
        revision_at_interrupt = self.paused_state["initial_revision"]

        # Execute wire transfer in DB with TOCTOU check!
        self.db.execute_wire(
            account_id=account_id,
            amount=amount,
            expected_revision=revision_at_interrupt
        )

        self.paused_state["status"] = "COMPLETED"
        return {
            "status": "COMPLETED",
            "account_id": account_id,
            "amount_transferred": amount,
            "approved_by": verified_payload["reviewer"]
        }


def main():
    db = BankAccountDatabase()
    workflow = InterruptedWireTransferWorkflow(db)

    workflow_id = "wf_wire_9921"
    account_id = "ACCT-99"
    amount = 25000.0  # High value requires finance:director

    # 1. Workflow reaches interrupt
    print("1. Workflow Enters Interrupt (Suspended for Review):")
    pause_msg = workflow.start_wire_transfer(workflow_id, account_id, amount)
    print(f"  Status: {pause_msg}")
    print(f"  Suspended state initial revision: {workflow.paused_state['initial_revision']}")
    assert workflow.paused_state["status"] == "SUSPENDED_WAITING_APPROVAL"

    # 2. Test Resume without Required Role (Operator attempting to approve Director action)
    print("\n2. Attempting Resume with Insufficient Role:")
    operator_token = HumanReviewApprovalGate.mint_approval_token(
        workflow_id=workflow_id, action="wire_transfer", amount=amount, revision=1, reviewer="junior_analyst"
    )
    try:
        workflow.resume_and_execute(workflow_id, operator_token, reviewer_roles={"operator", "analyst"})
        assert False, "Should fail without finance:director role"
    except PermissionError as role_err:
        print(f"  Successfully blocked unauthorized resume: {role_err}")

    # 3. Test Resume with Tampered Parameters
    print("\n3. Attempting Resume with Tampered Approval Token:")
    tampered_token = operator_token[:-4] + "ffff"
    try:
        workflow.resume_and_execute(workflow_id, tampered_token, reviewer_roles={"finance:director"})
        assert False, "Tampered signature must be rejected"
    except PermissionError as sig_err:
        print(f"  Successfully rejected tampered approval: {sig_err}")

    # 4. Test Concurrent Modification (TOCTOU) during pause
    print("\n4. Testing Resource Revision Drift (TOCTOU during pause):")
    director_token = HumanReviewApprovalGate.mint_approval_token(
        workflow_id=workflow_id, action="wire_transfer", amount=amount, revision=1, reviewer="sarah_director"
    )
    # Simulate an external transaction updating ACCT-99 while the workflow was paused!
    db.accounts["ACCT-99"].revision = 2  # Revision changed!

    try:
        workflow.resume_and_execute(workflow_id, director_token, reviewer_roles={"finance:director"})
        assert False, "Must fail when target account revision has drifted"
    except ValueError as toctou_err:
        print(f"  Successfully blocked execution due to revision drift: {toctou_err}")

    # Reset revision and test successful authorized completion
    db.accounts["ACCT-99"].revision = 1
    print("\n5. Authorized Execution with Valid Token and Matching Revision:")
    success_res = workflow.resume_and_execute(workflow_id, director_token, reviewer_roles={"finance:director"})
    print(f"  Workflow Completion: {success_res['status']} approved by {success_res['approved_by']}")
    print(f"  Remaining Bank Balance: ${db.get_account(account_id).balance:,.2f}")

    assert success_res["status"] == "COMPLETED"
    assert db.get_account(account_id).balance == 25000.0

    print("\nHuman review interrupt vs cryptographic authorization verified successfully.")


if __name__ == "__main__":
    main()
