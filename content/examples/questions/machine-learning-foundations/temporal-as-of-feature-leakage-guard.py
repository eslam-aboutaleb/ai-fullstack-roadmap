#!/usr/bin/env python3
"""
Executable test suite demonstrating point-in-time feature validity and preventing
temporal leakage across prediction boundaries.

Addresses Interview Question 927:
"What makes a feature unavailable at prediction time even when it exists in the table?"
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class CustomerTicketRecord:
    ticket_id: str
    created_at: datetime
    # Columns populated during the life of the ticket
    customer_tier: str          # Available at created_at
    initial_priority: str       # Available at created_at
    escalated_at: Optional[datetime]  # Ground-truth target (did it escalate?)
    resolution_code: Optional[str]    # Populated ONLY upon ticket close (FUTURE LEAKAGE)
    final_agent_notes: Optional[str]  # Populated ONLY upon escalation/close (FUTURE LEAKAGE)


class FeatureExtractionPipeline:
    """
    Simulates feature extraction for an automated ticket escalation prediction model.
    The decision must be made at T_decision = created_at (immediate automated routing).
    """

    @staticmethod
    def extract_leaky_features(ticket: CustomerTicketRecord) -> Dict[str, Any]:
        """
        Anti-pattern: Pulling all columns currently present in the production data warehouse table.
        Features like 'resolution_code' or 'final_agent_notes' only exist because the ticket was resolved/escalated.
        """
        return {
            "tier_enterprise": 1.0 if ticket.customer_tier == "enterprise" else 0.0,
            "priority_high": 1.0 if ticket.initial_priority == "high" else 0.0,
            # LEAKAGE: resolution_code is populated after escalation!
            "has_escalation_resolution": 1.0 if ticket.resolution_code == "ESCALATED_L2" else 0.0,
            "has_agent_notes": 1.0 if ticket.final_agent_notes is not None else 0.0,
        }

    @staticmethod
    def extract_point_in_time_features(
        ticket: CustomerTicketRecord,
        as_of_time: datetime
    ) -> Dict[str, Any]:
        """
        Production pattern: As-of temporal guard.
        Only features recorded at or strictly before as_of_time (T_decision) are permitted.
        """
        # Guard: Invariant check that the event itself has occurred
        if ticket.created_at > as_of_time:
            raise ValueError(f"Cannot score ticket {ticket.ticket_id} before creation timestamp {ticket.created_at}")

        # Features known at as_of_time
        return {
            "tier_enterprise": 1.0 if ticket.customer_tier == "enterprise" else 0.0,
            "priority_high": 1.0 if ticket.initial_priority == "high" else 0.0,
            # Leakage fields are strictly excluded or masked as unobservable
        }


def run_test_suite() -> None:
    t0 = datetime(2026, 10, 1, 9, 0, 0, tzinfo=timezone.utc)
    t_escalated = datetime(2026, 10, 1, 11, 30, 0, tzinfo=timezone.utc)
    t_resolved = datetime(2026, 10, 1, 14, 0, 0, tzinfo=timezone.utc)

    # Ticket 1: Escalated customer issue
    t1 = CustomerTicketRecord(
        ticket_id="TICK-101",
        created_at=t0,
        customer_tier="enterprise",
        initial_priority="high",
        escalated_at=t_escalated,
        resolution_code="ESCALATED_L2",
        final_agent_notes="Transferred to senior tier 3 on-call team."
    )

    # Ticket 2: Standard non-escalated ticket
    t2 = CustomerTicketRecord(
        ticket_id="TICK-102",
        created_at=t0,
        customer_tier="standard",
        initial_priority="low",
        escalated_at=None,
        resolution_code="RESOLVED_DOCS",
        final_agent_notes=None
    )

    # 1. Demonstrate Leaky Offline Features:
    leaky_t1 = FeatureExtractionPipeline.extract_leaky_features(t1)
    leaky_t2 = FeatureExtractionPipeline.extract_leaky_features(t2)

    # Notice how 'has_escalation_resolution' is an exact 1.0 proxy for the target:
    assert leaky_t1["has_escalation_resolution"] == 1.0
    assert leaky_t2["has_escalation_resolution"] == 0.0
    # An offline model trained with this feature achieves 100% test accuracy trivially!

    # 2. Simulate Production Runtime Reality (T_decision = t0 when ticket is created):
    # At t0, resolution_code does NOT exist yet in the operational transaction database.
    # If the production inference service runs at t0:
    pit_t1 = FeatureExtractionPipeline.extract_point_in_time_features(t1, as_of_time=t0)
    pit_t2 = FeatureExtractionPipeline.extract_point_in_time_features(t2, as_of_time=t0)

    # PIT features contain only valid observable predictors:
    assert "has_escalation_resolution" not in pit_t1
    assert "has_agent_notes" not in pit_t1
    assert pit_t1["tier_enterprise"] == 1.0
    assert pit_t1["priority_high"] == 1.0

    assert pit_t2["tier_enterprise"] == 0.0
    assert pit_t2["priority_high"] == 0.0

    # 3. Test Temporal Causality Invariant (cannot evaluate future tickets):
    try:
        past_time = datetime(2026, 10, 1, 8, 0, 0, tzinfo=timezone.utc)
        FeatureExtractionPipeline.extract_point_in_time_features(t1, as_of_time=past_time)
        assert False, "Should have raised ValueError on future event"
    except ValueError as e:
        assert "Cannot score ticket" in str(e)

    print("All temporal as-of feature leakage guard assertions verified successfully.")


if __name__ == "__main__":
    run_test_suite()

