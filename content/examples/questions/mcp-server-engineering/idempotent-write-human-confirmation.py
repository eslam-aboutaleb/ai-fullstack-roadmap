"""MCP write tool safety, business-level idempotency, and human-in-the-loop confirmation.

Demonstrates:
1. End-to-end idempotency key management: Deduplicating retries and rejecting parameter divergence conflicts.
2. Optimistic Concurrency Control (OCC): Guarding state updates with expected revision tokens.
3. Two-phase human confirmation for destructive mutations:
   - Phase 1 (prepare): Generates a cryptographically signed HMAC approval token with expiration.
   - Phase 2 (execute): Requires verified human confirmation token, defending against forged targets and repeat replays.
"""
from typing import Any, Dict, Optional, Tuple
import hashlib
import hmac
import json
import time

class IdempotentAccountService:
    HMAC_SECRET = b"write-capability-hmac-key-32b"

    def __init__(self):
        # Database accounts table: account_id -> {balance, revision}
        self._accounts: Dict[str, Dict[str, Any]] = {
            "acc_100": {"balance": 1000.0, "revision": 1},
            "acc_200": {"balance": 500.0, "revision": 4}
        }
        # Idempotency log: key -> {status, request_hash, response_payload}
        self._idempotency_store: Dict[str, Dict[str, Any]] = {}

    def transfer_funds(self, idempotency_key: str, from_acc: str, to_acc: str, amount: float, expected_revision: int) -> Dict[str, Any]:
        req_hash = hashlib.sha256(f"{from_acc}:{to_acc}:{amount}".encode()).hexdigest()

        # 1. Idempotency Check
        if idempotency_key in self._idempotency_store:
            record = self._idempotency_store[idempotency_key]
            if record["request_hash"] != req_hash:
                raise ValueError("Idempotency Conflict: Key reused with different transfer parameters!")
            # Safe replay: return cached authoritative outcome
            return record["response_payload"]

        # 2. Account verification
        if from_acc not in self._accounts or to_acc not in self._accounts:
            raise KeyError("One or both accounts do not exist.")

        sender = self._accounts[from_acc]

        # 3. Optimistic Concurrency Check
        if sender["revision"] != expected_revision:
            raise RuntimeError(f"Concurrency Conflict: Account revision is {sender['revision']}, expected {expected_revision}.")

        if sender["balance"] < amount:
            raise ValueError("Insufficient balance.")

        # 4. Atomic execution
        sender["balance"] -= amount
        sender["revision"] += 1
        self._accounts[to_acc]["balance"] += amount
        self._accounts[to_acc]["revision"] += 1

        response = {
            "status": "COMPLETED",
            "transfer_id": f"txn_{idempotency_key}",
            "from_account": from_acc,
            "new_balance": sender["balance"],
            "new_revision": sender["revision"]
        }

        # Cache outcome under idempotency key
        self._idempotency_store[idempotency_key] = {
            "request_hash": req_hash,
            "response_payload": response
        }
        return response

    # --- TWO-PHASE HUMAN CONFIRMATION CAPABILITY ---
    def prepare_destructive_closure(self, account_id: str, operator_id: str, ttl_seconds: int = 300) -> Dict[str, Any]:
        """Phase 1: Prepares closure and issues signed approval token."""
        if account_id not in self._accounts:
            raise KeyError(f"Account '{account_id}' does not exist.")

        expiry = int(time.time()) + ttl_seconds
        payload = f"{account_id}:{operator_id}:{expiry}"
        signature = hmac.new(self.HMAC_SECRET, payload.encode(), hashlib.sha256).hexdigest()

        return {
            "status": "AWAITING_HUMAN_CONFIRMATION",
            "account_id": account_id,
            "balance_to_liquidate": self._accounts[account_id]["balance"],
            "approval_token": f"{payload}:{signature}",
            "expires_at": expiry,
            "human_prompt": f"Authorize immediate irreversible closure of account '{account_id}'? [Confirm/Deny]"
        }

    def execute_destructive_closure(self, approval_token: str) -> Dict[str, Any]:
        """Phase 2: Validates signed approval token and executes deletion."""
        parts = approval_token.split(":")
        if len(parts) != 4:
            raise ValueError("Malformed approval token structure.")

        account_id, operator_id, expiry_str, signature = parts
        payload = f"{account_id}:{operator_id}:{expiry_str}"
        expected_sig = hmac.new(self.HMAC_SECRET, payload.encode(), hashlib.sha256).hexdigest()

        # Defend against forgery
        if not hmac.compare_digest(signature, expected_sig):
            raise PermissionError("Forged or tampered approval token! Signature verification failed.")

        # Check expiration
        if time.time() > int(expiry_str):
            raise TimeoutError("Approval token has expired. Re-initiate human approval.")

        if account_id not in self._accounts:
            raise KeyError("Account already deleted or missing.")

        del self._accounts[account_id]
        return {
            "status": "DELETED",
            "account_id": account_id,
            "closed_by": operator_id,
            "message": "Account liquidated and closed permanently."
        }

if __name__ == "__main__":
    service = IdempotentAccountService()

    # 1. Successful transfer
    res1 = service.transfer_funds(
        idempotency_key="key_tx_001",
        from_acc="acc_100",
        to_acc="acc_200",
        amount=150.0,
        expected_revision=1
    )
    assert res1["status"] == "COMPLETED"
    assert res1["new_balance"] == 850.0
    assert res1["new_revision"] == 2

    # 2. Idempotent Retry: Same key returns identical response without deducting funds twice!
    res_retry = service.transfer_funds(
        idempotency_key="key_tx_001",
        from_acc="acc_100",
        to_acc="acc_200",
        amount=150.0,
        expected_revision=1
    )
    assert res_retry == res1
    # Balance remains 850.0 (NOT deducted again to 700.0!)
    assert service._accounts["acc_100"]["balance"] == 850.0

    # 3. Idempotency Conflict: Reusing key with different amount is rejected!
    try:
        service.transfer_funds(
            idempotency_key="key_tx_001",
            from_acc="acc_100",
            to_acc="acc_200",
            amount=999.0,
            expected_revision=2
        )
        assert False, "Should have thrown idempotency conflict"
    except ValueError as ve:
        assert "Idempotency Conflict" in str(ve)

    # 4. Optimistic concurrency conflict rejection
    try:
        service.transfer_funds(
            idempotency_key="key_tx_002",
            from_acc="acc_100",
            to_acc="acc_200",
            amount=50.0,
            expected_revision=1  # Outdated! Revision is now 2
        )
        assert False, "Should have thrown concurrency conflict"
    except RuntimeError as re:
        assert "Concurrency Conflict" in str(re)

    # 5. Two-phase human approval workflow
    prep = service.prepare_destructive_closure("acc_200", operator_id="admin_user")
    assert prep["status"] == "AWAITING_HUMAN_CONFIRMATION"
    token = prep["approval_token"]

    # Tampered token rejected
    try:
        service.execute_destructive_closure(token.replace("acc_200", "acc_100"))
        assert False, "Should have caught forged token"
    except PermissionError as pe:
        assert "Signature verification failed" in str(pe)

    # Valid token succeeds
    closed = service.execute_destructive_closure(token)
    assert closed["status"] == "DELETED"
    assert "acc_200" not in service._accounts

    print("Idempotent write tools and two-phase human confirmation verified successfully.")

