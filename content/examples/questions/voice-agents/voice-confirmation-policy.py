"""Voice Confirmation Policy for Sensitive Operations.

Demonstrates formal authorization protocols for sensitive voice-driven actions.
Distinguishes high ASR phonetic confidence from authorization, enforces exact
parameter readback, and invalidates confirmation state upon parameter mutation.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class OperationStatus(str, Enum):
    AWAITING_CONFIRMATION = "awaiting_confirmation"
    CONFIRMED = "confirmed"
    COMMITTED = "committed"
    REJECTED = "rejected"


@dataclass
class TransactionProposal:
    transaction_id: str
    recipient: str
    amount_usd: float
    parameters_read_back_to_user: bool = False
    is_confirmed_by_user: bool = False
    principal_authenticated: bool = False
    asr_confidence_score: float = 0.0
    status: OperationStatus = OperationStatus.AWAITING_CONFIRMATION


class VoiceConfirmationEngine:
    """Manages sensitive transaction confirmation workflows and parameter invalidation."""

    def __init__(self) -> None:
        self.active_transactions: Dict[str, TransactionProposal] = {}
        self.audit_log: List[str] = []

    def propose_transaction(
        self, tx_id: str, recipient: str, amount_usd: float, principal_auth: bool
    ) -> TransactionProposal:
        tx = TransactionProposal(
            transaction_id=tx_id,
            recipient=recipient,
            amount_usd=amount_usd,
            principal_authenticated=principal_auth,
        )
        self.active_transactions[tx_id] = tx
        return tx

    def read_back_parameters(self, tx_id: str) -> str:
        """Agent reads back exact transaction parameters to the user."""
        tx = self.active_transactions[tx_id]
        tx.parameters_read_back_to_user = True
        return f"Ready to transfer ${tx.amount_usd:.2f} to {tx.recipient}. Please say confirm."

    def mutate_parameter(self, tx_id: str, new_amount_usd: float) -> str:
        """If user modifies any parameter, invalidate any pending confirmation!"""
        tx = self.active_transactions[tx_id]
        tx.amount_usd = new_amount_usd
        # INVARIANT: Parameter modification invalidates confirmation and readback!
        tx.parameters_read_back_to_user = False
        tx.is_confirmed_by_user = False
        tx.status = OperationStatus.AWAITING_CONFIRMATION
        return f"Updated amount to ${new_amount_usd:.2f}. Must re-confirm new parameters."

    def submit_spoken_confirmation(
        self, tx_id: str, spoken_word: str, asr_confidence: float
    ) -> Tuple[bool, str]:
        tx = self.active_transactions[tx_id]
        tx.asr_confidence_score = asr_confidence

        # Invariant 1: Principal must be authenticated (e.g. voice biometrics or session PIN)
        if not tx.principal_authenticated:
            return False, "AUTH_REQUIRED: Principal identity not verified."

        # Invariant 2: Current parameters must have been read back
        if not tx.parameters_read_back_to_user:
            return False, "PARAMETER_READBACK_MISSING: New parameters were not read back."

        # Invariant 3: High ASR confidence alone is insufficient if word is not explicit confirmation
        if spoken_word.lower() not in {"confirm", "yes, confirm", "approve"}:
            return False, f"AMBIGUOUS_CONFIRMATION: '{spoken_word}' is not an explicit approval."

        if asr_confidence < 0.90:
            return False, f"LOW_ASR_CONFIDENCE: Score {asr_confidence} < 0.90 required."

        tx.is_confirmed_by_user = True
        tx.status = OperationStatus.CONFIRMED
        return True, "Confirmation accepted."

    def commit_transaction(self, tx_id: str) -> Tuple[bool, str]:
        tx = self.active_transactions[tx_id]
        if (
            tx.status == OperationStatus.CONFIRMED
            and tx.principal_authenticated
            and tx.parameters_read_back_to_user
            and tx.is_confirmed_by_user
        ):
            tx.status = OperationStatus.COMMITTED
            self.audit_log.append(f"Committed {tx_id}: ${tx.amount_usd} to {tx.recipient}")
            return True, f"Successfully transferred ${tx.amount_usd} to {tx.recipient}."
        return False, "COMMIT_REJECTED: Preconditions for sensitive operation not satisfied."


def test_voice_confirmation_policy() -> None:
    engine = VoiceConfirmationEngine()

    # Step 1: Propose $100 transfer to Alice
    tx = engine.propose_transaction(
        tx_id="tx_9901", recipient="Alice", amount_usd=100.0, principal_auth=True
    )
    assert tx.status == OperationStatus.AWAITING_CONFIRMATION

    # Step 2: Attempting to commit without readback or confirmation fails
    ok_commit_premature, _ = engine.commit_transaction("tx_9901")
    assert ok_commit_premature is False

    # Step 3: Agent reads back parameters
    readback = engine.read_back_parameters("tx_9901")
    assert "Ready to transfer $100.00 to Alice" in readback
    assert tx.parameters_read_back_to_user is True

    # Step 4: User changes mind: "Make it $250 instead"
    msg_mutate = engine.mutate_parameter("tx_9901", new_amount_usd=250.0)
    assert tx.amount_usd == 250.0
    assert tx.parameters_read_back_to_user is False  # Invalidation asserted!

    # Step 5: User says "Yes" with 99% ASR confidence before agent reads back new amount
    ok_conf_stale, reason_stale = engine.submit_spoken_confirmation(
        "tx_9901", spoken_word="confirm", asr_confidence=0.99
    )
    # INVARIANT: Must reject confirmation because new parameters weren't read back!
    assert ok_conf_stale is False
    assert "PARAMETER_READBACK_MISSING" in reason_stale

    # Step 6: Read back updated parameters and confirm with high confidence
    engine.read_back_parameters("tx_9901")
    assert tx.parameters_read_back_to_user is True

    ok_conf, msg_conf = engine.submit_spoken_confirmation(
        "tx_9901", spoken_word="confirm", asr_confidence=0.98
    )
    assert ok_conf is True
    assert tx.status == OperationStatus.CONFIRMED

    # Step 7: Commit transaction safely
    ok_commit, msg_commit = engine.commit_transaction("tx_9901")
    assert ok_commit is True
    assert tx.status == OperationStatus.COMMITTED
    assert len(engine.audit_log) == 1

    print(
        f"Voice confirmation policy verified: parameters_verified=True, "
        f"stale_confirmation_prevented=True, committed_amount=${tx.amount_usd:.2f}"
    )


if __name__ == "__main__":
    test_voice_confirmation_policy()
