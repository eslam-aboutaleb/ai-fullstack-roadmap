"""Human-in-the-loop workflow suspension, cryptographic approval tokens, and validated resumption.

Demonstrates:
1. Durable workflow suspension at decision gates: Transitioning to SUSPENDED_WAITING_APPROVAL without blocking worker threads.
2. Cryptographic approval tokens: Binding workflow ID, operation hash, target resource revision, and expiration into a signed token.
3. Parameter tampering and stale revision detection: Aborting resumption if the target resource was modified while waiting.
4. Role-based reviewer authorization on resume callback.
"""
from typing import Any, Dict, Optional, Tuple
import hashlib
import hmac
import json
import time

class HumanInTheLoopOrchestrator:
    SECRET_KEY = b"human-approval-gate-secret-32b"

    def __init__(self):
        # Database of workflows: workflow_id -> {state, pending_action, target_revision}
        self.workflows: Dict[str, Dict[str, Any]] = {}

    def suspend_for_approval(
        self,
        workflow_id: str,
        action_name: str,
        parameters: Dict[str, Any],
        target_resource_id: str,
        current_revision: int,
        ttl_seconds: int = 300
    ) -> Dict[str, Any]:
        """Pauses workflow execution and mints a cryptographically bound approval token."""
        expiry = int(time.time()) + ttl_seconds
        param_hash = hashlib.sha256(json.dumps(parameters, sort_keys=True).encode()).hexdigest()

        # Token payload: workflow_id:action:resource:rev:param_hash:expiry
        payload = f"{workflow_id}:{action_name}:{target_resource_id}:{current_revision}:{param_hash}:{expiry}"
        signature = hmac.new(self.SECRET_KEY, payload.encode(), hashlib.sha256).hexdigest()
        approval_token = f"{payload}.{signature}"

        # Persist suspended state
        self.workflows[workflow_id] = {
            "status": "SUSPENDED_WAITING_APPROVAL",
            "action": action_name,
            "target_resource": target_resource_id,
            "required_revision": current_revision,
            "param_hash": param_hash,
            "parameters": parameters,
            "expires_at": expiry
        }

        return {
            "workflow_id": workflow_id,
            "status": "SUSPENDED_WAITING_APPROVAL",
            "approval_token": approval_token,
            "expires_at": expiry,
            "human_summary": f"Approval requested: {action_name} on {target_resource_id} (Rev {current_revision})"
        }

    def resume_with_approval(
        self,
        approval_token: str,
        reviewer_id: str,
        reviewer_role: str,
        current_live_resource_revision: int
    ) -> Dict[str, Any]:
        """Validates reviewer credentials, token signature, and live resource revision before resuming."""
        parts = approval_token.split(".")
        if len(parts) != 2:
            raise ValueError("Malformed approval token.")

        payload, signature = parts
        expected_sig = hmac.new(self.SECRET_KEY, payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected_sig):
            raise PermissionError("Approval token verification failed: Token forged or tampered with.")

        wf_id, action, resource, expected_rev_str, p_hash, expiry_str = payload.split(":")
        expected_rev = int(expected_rev_str)
        expiry = int(expiry_str)

        if wf_id not in self.workflows:
            raise KeyError(f"Workflow '{wf_id}' not found.")

        wf_record = self.workflows[wf_id]

        # 1. State check
        if wf_record["status"] != "SUSPENDED_WAITING_APPROVAL":
            raise RuntimeError(f"Workflow cannot be resumed from state '{wf_record['status']}'.")

        # 2. Expiration check
        if time.time() > expiry:
            wf_record["status"] = "EXPIRED"
            raise TimeoutError("Approval token has expired.")

        # 3. Role check: Reviewer must have manager/admin role
        if reviewer_role not in {"manager", "admin"}:
            raise PermissionError(f"Reviewer '{reviewer_id}' with role '{reviewer_role}' lacks authority to approve.")

        # 4. CRITICAL CONCURRENCY CHECK: Has the target resource been modified while waiting?
        if current_live_resource_revision != expected_rev:
            wf_record["status"] = "ABORTED_STALE_REVISION"
            raise RuntimeError(
                f"Concurrency Conflict: Target resource '{resource}' advanced from revision "
                f"{expected_rev} to {current_live_resource_revision} while waiting for review. Approval invalidated!"
            )

        # 5. Successfully resume workflow
        wf_record["status"] = "COMPLETED"
        wf_record["approved_by"] = reviewer_id
        return {
            "workflow_id": wf_id,
            "status": "COMPLETED",
            "executed_action": action,
            "approved_by": reviewer_id,
            "message": "Workflow successfully resumed and mutation committed."
        }

if __name__ == "__main__":
    orchestrator = HumanInTheLoopOrchestrator()

    # 1. Suspend workflow for high-impact action (Database Schema Migration)
    gate = orchestrator.suspend_for_approval(
        workflow_id="wf_migration_42",
        action_name="APPLY_INDEX_CONCURRENTLY",
        parameters={"table": "customers", "index": "idx_email"},
        target_resource_id="db_cluster_prod",
        current_revision=5,
        ttl_seconds=300
    )
    assert gate["status"] == "SUSPENDED_WAITING_APPROVAL"
    token = gate["approval_token"]

    # 2. Unauthorized Reviewer Attempt is BLOCKED
    try:
        orchestrator.resume_with_approval(
            approval_token=token,
            reviewer_id="intern_dave",
            reviewer_role="viewer",
            current_live_resource_revision=5
        )
        assert False, "Should reject unauthorized reviewer"
    except PermissionError as pe:
        assert "lacks authority" in str(pe)

    # 3. Target Resource Modified While Waiting (Stale Revision Conflict BLOCKED)
    try:
        orchestrator.resume_with_approval(
            approval_token=token,
            reviewer_id="lead_eng",
            reviewer_role="admin",
            current_live_resource_revision=6  # Revision advanced from 5 -> 6!
        )
        assert False, "Should reject stale revision"
    except RuntimeError as re:
        assert "advanced from revision 5 to 6" in str(re)

    # 4. Valid Approval resumes and commits workflow
    gate2 = orchestrator.suspend_for_approval(
        workflow_id="wf_migration_43",
        action_name="APPLY_INDEX_CONCURRENTLY",
        parameters={"table": "orders", "index": "idx_user"},
        target_resource_id="db_cluster_prod",
        current_revision=6
    )
    res_ok = orchestrator.resume_with_approval(
        approval_token=gate2["approval_token"],
        reviewer_id="lead_eng",
        reviewer_role="admin",
        current_live_resource_revision=6
    )
    assert res_ok["status"] == "COMPLETED"
    assert res_ok["approved_by"] == "lead_eng"

    print("Human-in-the-loop workflow suspension and cryptographic resumption verified successfully.")
