"""Human Handoff Protocol: Structured State Machine vs Naive Prompt Sentences.

Demonstrates:
1. Why Naive Prompt Handoff Fails:
   - A prompt sentence ('If the user wants a human, transfer them') only produces conversational text;
     it does not notify support queues, persist ticket state, or block further agent output.
2. Production Handoff Protocol:
   - Explicit state machine: `AUTONOMOUS` -> `PAUSED_FOR_HUMAN` -> `HUMAN_RESOLVED`.
   - Structured Handoff Ticket: captures session history, sentiment score, detected intent,
     confidence level, and pending business actions.
   - Guarded Gateway: rejects further autonomous agent responses while the session is paused for human review.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import json
from typing import Any, Dict, List, Optional


class SessionHandoffState(Enum):
    AUTONOMOUS = "AUTONOMOUS"
    PAUSED_FOR_HUMAN = "PAUSED_FOR_HUMAN"
    HUMAN_ACTIVE = "HUMAN_ACTIVE"
    RESOLVED = "RESOLVED"


@dataclass
class HandoffTicket:
    ticket_id: str
    session_id: str
    customer_id: str
    reason: str
    detected_intent: str
    confidence_score: float
    sentiment_flag: str  # "FRUSTRATED", "ESCALATION_REQUESTED", "POLICY_RESTRICTION"
    conversation_summary: str
    pending_action: Optional[Dict[str, Any]] = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class HumanSupportQueue:
    """Mock CRM / human ticketing service (Zendesk / Salesforce)."""

    def __init__(self):
        self.tickets: Dict[str, HandoffTicket] = {}

    def create_ticket(self, ticket: HandoffTicket) -> str:
        self.tickets[ticket.ticket_id] = ticket
        return ticket.ticket_id


class CustomerAgentWithHandoff:
    """Agent implementing explicit human handoff protocol."""

    def __init__(self, session_id: str, customer_id: str, support_queue: HumanSupportQueue):
        self.session_id = session_id
        self.customer_id = customer_id
        self.queue = support_queue
        self.state = SessionHandoffState.AUTONOMOUS
        self.active_ticket_id: Optional[str] = None
        self.history: List[Dict[str, str]] = []

    def handle_message(self, user_text: str) -> str:
        # Invariant: Block autonomous responses if session is paused for human!
        if self.state in (SessionHandoffState.PAUSED_FOR_HUMAN, SessionHandoffState.HUMAN_ACTIVE):
            raise PermissionError(
                f"Agent response blocked: session is in '{self.state.value}'. "
                "Autonomous model is silenced while awaiting human intervention."
            )

        self.history.append({"role": "user", "content": user_text})

        # Check for handoff condition (e.g. repeated frustration or explicit demand)
        if "human" in user_text.lower() or "supervisor" in user_text.lower() or "dispute" in user_text.lower():
            return self._initiate_protocol_handoff(
                reason="Customer requested escalation regarding disputed transaction",
                sentiment="ESCALATION_REQUESTED"
            )

        reply = f"Autonomous response: I can help with '{user_text}'"
        self.history.append({"role": "assistant", "content": reply})
        return reply

    def _initiate_protocol_handoff(self, reason: str, sentiment: str) -> str:
        ticket_id = f"TICK-{self.session_id[-4:]}-88"
        ticket = HandoffTicket(
            ticket_id=ticket_id,
            session_id=self.session_id,
            customer_id=self.customer_id,
            reason=reason,
            detected_intent="TRANSACTION_DISPUTE",
            confidence_score=0.42,  # Low confidence triggered escalation
            sentiment_flag=sentiment,
            conversation_summary="Customer attempted dispute resolution; requested human supervisor.",
            pending_action={"action": "waive_late_fee", "amount": 35.00}
        )

        self.queue.create_ticket(ticket)
        self.active_ticket_id = ticket_id
        # Advance state machine!
        self.state = SessionHandoffState.PAUSED_FOR_HUMAN

        farewell = (
            "I have transferred your case to a human support supervisor with full context. "
            f"Ticket #{ticket_id} has been opened. An agent will be with you shortly."
        )
        self.history.append({"role": "assistant", "content": farewell})
        return farewell

    def human_agent_resolves(self, supervisor_name: str, resolution_message: str):
        """Human supervisor takes over and resolves the ticket."""
        self.state = SessionHandoffState.RESOLVED
        self.history.append({"role": "human_agent", "content": f"[{supervisor_name}]: {resolution_message}"})


def main():
    queue = HumanSupportQueue()
    agent = CustomerAgentWithHandoff(
        session_id="sess_cust_1092",
        customer_id="cust_9921",
        support_queue=queue
    )

    # 1. Normal autonomous interaction
    reply1 = agent.handle_message("What are your business hours?")
    print("1. Autonomous Response:")
    print(f"  Reply: '{reply1}'")
    print(f"  State: {agent.state.value}")
    assert agent.state == SessionHandoffState.AUTONOMOUS

    # 2. Trigger Handoff
    print("\n2. Triggering Structured Handoff:")
    reply2 = agent.handle_message("I demand to speak with a human supervisor about an unauthorized charge!")
    print(f"  Reply: '{reply2}'")
    print(f"  State: {agent.state.value}")
    assert agent.state == SessionHandoffState.PAUSED_FOR_HUMAN
    assert agent.active_ticket_id in queue.tickets

    ticket = queue.tickets[agent.active_ticket_id]
    print(f"  Created Ticket ID: {ticket.ticket_id}")
    print(f"  Ticket Intent: {ticket.detected_intent} (Confidence: {ticket.confidence_score})")
    print(f"  Pending Action: {ticket.pending_action}")

    # 3. Verify Guard: Autonomous agent is strictly silenced while paused
    print("\n3. Testing Agent Silencing Invariant:")
    try:
        agent.handle_message("Hello? Are you still there?")
        assert False, "Autonomous agent must be silenced during human handoff pause"
    except PermissionError as err:
        print(f"  Successfully blocked rogue agent message: {err}")

    # 4. Human supervisor resolves the ticket
    print("\n4. Human Supervisor Resolves Case:")
    agent.human_agent_resolves("Supervisor Mark", "I have reviewed your disputed charge of $35.00 and waived the fee.")
    print(f"  Final State: {agent.state.value}")
    print(f"  Last Message: {agent.history[-1]['content']}")
    assert agent.state == SessionHandoffState.RESOLVED

    print("\nHuman handoff protocol and state machine invariants verified successfully.")


if __name__ == "__main__":
    main()
