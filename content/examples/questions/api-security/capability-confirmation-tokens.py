"""Capability confirmation tokens, parameter tamper-proofing, and single-use execution boundaries.

Demonstrates:
1. Treating high-impact confirmation tokens as cryptographic capabilities rather than simple booleans.
2. Cryptographic parameter binding: Any modification to target resource, operator identity, or payload parameters invalidates the capability.
3. Single-use replay protection and short-lived expiration deadlines.
"""
from typing import Any, Dict, Optional, Set
import hashlib
import hmac
import json
import time

class CapabilityTokenEngine:
    SECRET_KEY = b"high-privilege-action-hmac-secret-32b"

    def __init__(self):
        # Set of consumed single-use capability IDs (jti/nonce)
        self._consumed_capabilities: Set[str] = set()

    def issue_action_capability(
        self,
        action: str,
        target_id: str,
        operator_id: str,
        parameters: Dict[str, Any],
        ttl_seconds: int = 300
    ) -> str:
        """Issues an HMAC-signed capability token binding the exact action, target, and parameters."""
        nonce = f"nonce_{time.time_ns()}"
        expiry = int(time.time()) + ttl_seconds
        param_hash = hashlib.sha256(json.dumps(parameters, sort_keys=True).encode()).hexdigest()

        payload = {
            "action": action,
            "target": target_id,
            "operator": operator_id,
            "param_hash": param_hash,
            "nonce": nonce,
            "exp": expiry
        }
        payload_b64 = json.dumps(payload).encode().hex()
        signature = hmac.new(self.SECRET_KEY, payload_b64.encode(), hashlib.sha256).hexdigest()
        return f"{payload_b64}.{signature}"

    def verify_and_consume_capability(
        self,
        token: str,
        expected_action: str,
        expected_target: str,
        expected_operator: str,
        actual_parameters: Dict[str, Any]
    ) -> bool:
        """Validates signature, expiration, parameter integrity, and single-use consumption."""
        parts = token.split(".")
        if len(parts) != 2:
            raise PermissionError("Malformed capability token.")

        payload_b64, signature = parts
        expected_sig = hmac.new(self.SECRET_KEY, payload_b64.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected_sig):
            raise PermissionError("Cryptographic signature failure: Capability token forged or altered.")

        payload = json.loads(bytes.fromhex(payload_b64).decode())

        # 1. Single-use replay defense
        nonce = payload["nonce"]
        if nonce in self._consumed_capabilities:
            raise PermissionError(f"Replay attack detected: Capability token '{nonce}' was already executed.")

        # 2. Expiration check
        if time.time() > payload["exp"]:
            raise TimeoutError("Capability token has expired.")

        # 3. Action, target, and operator binding
        if payload["action"] != expected_action:
            raise PermissionError(f"Action mismatch: Token granted for '{payload['action']}', not '{expected_action}'.")
        if payload["target"] != expected_target:
            raise PermissionError(f"Target mismatch: Token granted for '{payload['target']}', not '{expected_target}'.")
        if payload["operator"] != expected_operator:
            raise PermissionError(f"Operator mismatch: Token issued to '{payload['operator']}', not '{expected_operator}'.")

        # 4. Parameter Tampering Defense: Parameter hash must match exact execution arguments!
        actual_param_hash = hashlib.sha256(json.dumps(actual_parameters, sort_keys=True).encode()).hexdigest()
        if payload["param_hash"] != actual_param_hash:
            raise PermissionError("Parameter tampering detected: Execution parameters do not match approved capability parameters!")

        # Mark consumed atomically
        self._consumed_capabilities.add(nonce)
        return True

if __name__ == "__main__":
    engine = CapabilityTokenEngine()

    approved_params = {"destination_account": "acc_target_99", "amount": 10_000.0}

    # 1. Issue capability token
    cap_token = engine.issue_action_capability(
        action="TRANSFER_FUNDS",
        target_id="acc_source_11",
        operator_id="operator_alice",
        parameters=approved_params,
        ttl_seconds=120
    )

    # 2. Valid execution consumes capability
    assert engine.verify_and_consume_capability(
        token=cap_token,
        expected_action="TRANSFER_FUNDS",
        expected_target="acc_source_11",
        expected_operator="operator_alice",
        actual_parameters=approved_params
    ) is True

    # 3. Replay attack rejection: Using same token again is blocked!
    try:
        engine.verify_and_consume_capability(
            token=cap_token,
            expected_action="TRANSFER_FUNDS",
            expected_target="acc_source_11",
            expected_operator="operator_alice",
            actual_parameters=approved_params
        )
        assert False, "Should block replay attack"
    except PermissionError as pe:
        assert "Replay attack detected" in str(pe)

    # 4. Parameter Tampering Rejection: Attacker alters transfer amount from $10k to $100k
    tampered_token = engine.issue_action_capability(
        action="TRANSFER_FUNDS",
        target_id="acc_source_11",
        operator_id="operator_alice",
        parameters=approved_params
    )
    tampered_params = {"destination_account": "acc_target_99", "amount": 100_000.0}
    try:
        engine.verify_and_consume_capability(
            token=tampered_token,
            expected_action="TRANSFER_FUNDS",
            expected_target="acc_source_11",
            expected_operator="operator_alice",
            actual_parameters=tampered_params
        )
        assert False, "Should block parameter tampering"
    except PermissionError as pe:
        assert "Parameter tampering detected" in str(pe)

    print("Capability confirmation tokens and parameter tamper-proofing verified successfully.")
