"""Perception Invalidation Guard & Revision-Gated Tool Dispatch.

Demonstrates pre-dispatch precondition verification for live autonomous assistants.
When an external environment update (e.g. DOM shift, modal popup, price change)
invalidates the perceptual assumptions of an in-flight LLM reasoning plan, the dispatch
gateway detects the revision mismatch and rejects the obsolete action before side effects occur.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class ActionDispatchStatus(str, Enum):
    EXECUTED = "executed"
    REJECTED_STALE_PERCEPTION = "rejected_stale_perception"
    PRECONDITION_FAILED = "precondition_failed"


@dataclass(frozen=True)
class PerceptualObservation:
    observation_id: str
    revision: int
    element_id: str
    bounding_box: Tuple[int, int, int, int]  # (x1, y1, x2, y2)
    state_payload: Dict[str, Any]


@dataclass(frozen=True)
class ActionProposal:
    action_id: str
    target_element_id: str
    click_coordinates: Tuple[int, int]
    planned_against_revision: int
    intent: str


class LiveEnvironmentState:
    """Represents a dynamic live UI or market environment with advancing revisions."""

    def __init__(self) -> None:
        self.current_revision: int = 1
        self.elements: Dict[str, Dict[str, Any]] = {
            "btn_checkout": {
                "label": "Confirm & Pay $45",
                "bbox": (300, 500, 450, 550),
                "is_active": True,
            }
        }
        self.active_modals: List[str] = []

    def mutate_environment(self, reason: str, element_updates: Dict[str, Any]) -> int:
        """Environment mutation (e.g. promotional banner shifts layout, price updates)."""
        self.current_revision += 1
        for elem_id, new_attrs in element_updates.items():
            if elem_id in self.elements:
                self.elements[elem_id].update(new_attrs)
            else:
                self.elements[elem_id] = new_attrs
        return self.current_revision


class RevisionGatedDispatchGateway:
    """Pre-dispatch verification gate that rejects actions planned against obsolete perception."""

    def __init__(self, environment: LiveEnvironmentState) -> None:
        self.env = environment
        self.rejected_actions: List[Dict[str, Any]] = []
        self.executed_actions: List[Dict[str, Any]] = []

    def dispatch_action(self, proposal: ActionProposal) -> Tuple[ActionDispatchStatus, str]:
        # Precondition Gate 1: Check perceptual revision horizon
        if proposal.planned_against_revision < self.env.current_revision:
            reason = (
                f"STALE_PERCEPTION: Planned against revision {proposal.planned_against_revision}, "
                f"but current environment is at revision {self.env.current_revision}."
            )
            self.rejected_actions.append({"proposal": proposal, "reason": reason})
            return ActionDispatchStatus.REJECTED_STALE_PERCEPTION, reason

        # Precondition Gate 2: Element existence and coordinate sanity
        elem = self.env.elements.get(proposal.target_element_id)
        if not elem or not elem.get("is_active"):
            reason = f"ELEMENT_INVALID: Target {proposal.target_element_id} is no longer interactive."
            self.rejected_actions.append({"proposal": proposal, "reason": reason})
            return ActionDispatchStatus.PRECONDITION_FAILED, reason

        x, y = proposal.click_coordinates
        x1, y1, x2, y2 = elem["bbox"]
        if not (x1 <= x <= x2 and y1 <= y <= y2):
            reason = f"COORDINATE_DRIFT: Coordinates ({x}, {y}) fall outside current bbox {elem['bbox']}."
            self.rejected_actions.append({"proposal": proposal, "reason": reason})
            return ActionDispatchStatus.PRECONDITION_FAILED, reason

        # Commit action
        self.executed_actions.append({"proposal": proposal, "committed_revision": self.env.current_revision})
        return ActionDispatchStatus.EXECUTED, f"Action {proposal.action_id} executed successfully."


def test_perception_invalidation_guard() -> None:
    env = LiveEnvironmentState()
    gateway = RevisionGatedDispatchGateway(env)

    # 1. Agent takes perception snapshot at revision 1
    obs_rev1 = PerceptualObservation(
        observation_id="obs_01",
        revision=env.current_revision,  # revision 1
        element_id="btn_checkout",
        bounding_box=env.elements["btn_checkout"]["bbox"],  # (300, 500, 450, 550)
        state_payload={"price": 45},
    )
    assert obs_rev1.revision == 1

    # 2. Agent begins 2-second LLM reasoning to construct checkout plan
    # While reasoning is in flight, an unexpected popup banner appears, shifting DOM layout!
    # Bounding box shifts from (300, 500...) down to (300, 650...) and revision advances to 2
    new_rev = env.mutate_environment(
        reason="Promotional modal banner pushed layout down 150px",
        element_updates={
            "btn_checkout": {"bbox": (300, 650, 450, 700)},
            "banner_ad": {"bbox": (300, 500, 450, 600), "label": "Subscribe for 10% off"},
        },
    )
    assert new_rev == 2
    assert env.current_revision == 2

    # 3. Model finishes reasoning and emits proposal targeting old coordinates at revision 1
    stale_proposal = ActionProposal(
        action_id="act_checkout_click",
        target_element_id="btn_checkout",
        click_coordinates=(375, 525),  # Old center point (now overlaps the banner!)
        planned_against_revision=1,
        intent="Click checkout button to complete purchase",
    )

    # 4. Dispatch gate intercepts proposal and rejects it before side effects occur!
    status, message = gateway.dispatch_action(stale_proposal)
    assert status == ActionDispatchStatus.REJECTED_STALE_PERCEPTION
    assert "STALE_PERCEPTION" in message
    assert len(gateway.executed_actions) == 0
    assert len(gateway.rejected_actions) == 1

    # 5. Agent receives rejection, refreshes perception to Revision 2, and plans against fresh state
    obs_rev2 = PerceptualObservation(
        observation_id="obs_02",
        revision=env.current_revision,  # revision 2
        element_id="btn_checkout",
        bounding_box=env.elements["btn_checkout"]["bbox"],  # (300, 650, 450, 700)
        state_payload={"price": 45},
    )

    valid_proposal = ActionProposal(
        action_id="act_checkout_click_v2",
        target_element_id="btn_checkout",
        click_coordinates=(375, 675),  # Fresh center point matching Revision 2 bbox
        planned_against_revision=2,
        intent="Click checkout button to complete purchase",
    )

    status_v2, msg_v2 = gateway.dispatch_action(valid_proposal)
    assert status_v2 == ActionDispatchStatus.EXECUTED
    assert len(gateway.executed_actions) == 1

    print(
        f"Perception invalidation guard verified: stale_action_rejected=True, "
        f"freshened_action_executed=True, final_revision={env.current_revision}"
    )


if __name__ == "__main__":
    test_perception_invalidation_guard()

