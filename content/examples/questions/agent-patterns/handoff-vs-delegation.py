"""Handoff vs Delegation Pattern.

Demonstrates:
1. Delegation (Subroutine / RPC Model):
   - Primary coordinator retains 100% conversational and task ownership.
   - Worker is invoked as an internal sub-procedure, returns data, and coordinator continues talking to user.
2. Handoff (Relay / State Transfer Model):
   - Primary coordinator relinquishes active conversational ownership.
   - Serializes entire session state (conversation history, authenticated user ID, verified intent).
   - Enqueues into target recipient (e.g., Human Tier-2 Support or Autonomous Billing Agent).
   - Recipient becomes the new active owner responsible for all future user interaction.
3. Explicit ownership state machine preventing dual-responder race conditions or orphaned sessions.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import json
from typing import Any, Dict, List, Optional


class InteractionOwner(Enum):
    PRIMARY_CONCIERGE = "PRIMARY_CONCIERGE"
    HUMAN_SUPPORT_TIER2 = "HUMAN_SUPPORT_TIER2"
    FRAUD_INVESTIGATION = "FRAUD_INVESTIGATION"


@dataclass
class SessionState:
    session_id: str
    user_id: str
    current_owner: InteractionOwner
    history: List[Dict[str, str]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    handoff_records: List[Dict[str, Any]] = field(default_factory=list)


# --- 1. Delegation Subroutine ---
class CurrencyConverterSubroutine:
    """Delegated worker: pure function / subroutine. Has no conversational awareness."""

    RATES = {"EUR": 1.08, "GBP": 1.27, "JPY": 0.0067}

    @classmethod
    def convert_to_usd(cls, amount: float, currency: str) -> float:
        rate = cls.RATES.get(currency.upper(), 1.0)
        return round(amount * rate, 2)


# --- 2. Primary Concierge Agent ---
class ConciergeAgent:
    """Primary agent handling conversational user experience."""

    def __init__(self, session: SessionState):
        self.session = session

    def handle_user_message(self, message: str) -> str:
        # Enforce that only the declared owner can respond
        if self.session.current_owner != InteractionOwner.PRIMARY_CONCIERGE:
            raise PermissionError(
                f"Concierge cannot reply: active interaction owner is '{self.session.current_owner.value}'"
            )

        self.session.history.append({"role": "user", "text": message})

        # Scenario A: Delegation pattern (calculating currency conversion)
        if "convert" in message.lower():
            # Concierge retains ownership, calls subroutine as internal delegation
            converted = CurrencyConverterSubroutine.convert_to_usd(100.0, "EUR")
            reply = f"100 EUR is currently ${converted:.2f} USD."
            self.session.history.append({"role": "concierge", "text": reply})
            return reply

        # Scenario B: Handoff pattern (user requests human supervisor or reports fraud)
        if "human" in message.lower() or "fraud" in message.lower():
            return self.initiate_handoff(
                target=InteractionOwner.HUMAN_SUPPORT_TIER2,
                reason="User requested human escalation regarding transaction dispute"
            )

        reply = f"Concierge response to: '{message}'"
        self.session.history.append({"role": "concierge", "text": reply})
        return reply

    def initiate_handoff(self, target: InteractionOwner, reason: str) -> str:
        handoff_record = {
            "from_owner": self.session.current_owner.value,
            "to_owner": target.value,
            "reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dialogue_turns": len(self.session.history)
        }
        self.session.handoff_records.append(handoff_record)

        # Relinquish ownership!
        self.session.current_owner = target
        farewell = "I am transferring your case with full context to our Tier-2 Human Support team. Please hold."
        self.session.history.append({"role": "concierge", "text": farewell})
        return farewell


# --- 3. Recipient Human Support Queue ---
class HumanSupportQueue:
    """Target of handoff. Consumes serialized session and assumes primary responder role."""

    @classmethod
    def accept_and_respond(cls, session: SessionState, agent_name: str, message: str) -> str:
        if session.current_owner != InteractionOwner.HUMAN_SUPPORT_TIER2:
            raise ValueError(f"Session not assigned to Human Support Tier 2. Found: {session.current_owner}")

        response = f"[{agent_name} - Tier 2 Support]: {message}"
        session.history.append({"role": "human_agent", "text": response})
        return response


def main():
    session = SessionState(
        session_id="SESS-4040",
        user_id="USR-992",
        current_owner=InteractionOwner.PRIMARY_CONCIERGE
    )
    concierge = ConciergeAgent(session)

    # 1. Test Delegation: Concierge retains ownership across subroutine call
    reply1 = concierge.handle_user_message("Can you convert 100 EUR for me?")
    print("1. Delegation Pattern:")
    print(f"  User: 'Can you convert 100 EUR for me?'")
    print(f"  Concierge Reply: '{reply1}'")
    print(f"  Current Owner: {session.current_owner.value}")
    assert session.current_owner == InteractionOwner.PRIMARY_CONCIERGE, "Owner must remain Concierge during delegation"

    # 2. Test Handoff: Concierge initiates handoff and relinquishes ownership
    print("\n2. Handoff Initiation:")
    reply2 = concierge.handle_user_message("I want to speak with a human agent now.")
    print(f"  Concierge Reply: '{reply2}'")
    print(f"  Current Owner: {session.current_owner.value}")
    assert session.current_owner == InteractionOwner.HUMAN_SUPPORT_TIER2, "Owner must transition to HUMAN_SUPPORT_TIER2"
    assert len(session.handoff_records) == 1

    # 3. Test Ownership Invariant: Concierge is blocked from sending further messages
    print("\n3. Testing Ownership Invariant (Dual-Responder Prevention):")
    try:
        concierge.handle_user_message("Another message while handed off")
        assert False, "Concierge must not be allowed to respond after handoff"
    except PermissionError as err:
        print(f"  Successfully blocked concierge response: {err}")

    # 4. Human Support Agent takes over session and responds
    print("\n4. Target Agent Resumes Interaction:")
    human_reply = HumanSupportQueue.accept_and_respond(
        session,
        agent_name="Sarah",
        message="Hello! I see your conversation history and transaction. Let me assist you."
    )
    print(f"  Human Reply: '{human_reply}'")
    assert "Sarah" in human_reply
    assert len(session.history) == 5

    print("\nHandoff vs Delegation architectural distinction verified.")


if __name__ == "__main__":
    main()
