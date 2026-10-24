"""Portable Skill Contract Validator & Cross-Framework Compatibility.

Validates that an agent skill package satisfies portable input/output contracts,
enforces semantic versioning rules, and tests compatibility across different
agent execution runtimes without tight coupling to framework-specific APIs.
"""

from dataclasses import dataclass, field
import re
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass(frozen=True)
class SkillInputContract:
    parameter_name: str
    expected_type: str
    required: bool
    description: str


@dataclass(frozen=True)
class SkillOutputContract:
    field_name: str
    expected_type: str
    description: str


@dataclass
class PortableSkillContract:
    skill_name: str
    semantic_version: str  # e.g. "2.1.0"
    target_framework_adapter: str  # e.g. "universal_mcp_agent"
    required_host_tools: Set[str]
    inputs: List[SkillInputContract]
    outputs: List[SkillOutputContract]


class SkillContractValidator:
    """Validates skill contracts against host capabilities and runtime payloads."""

    SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")

    @classmethod
    def validate_contract_integrity(cls, contract: PortableSkillContract) -> Tuple[bool, str]:
        # Semver format check
        if not cls.SEMVER_PATTERN.match(contract.semantic_version):
            return False, f"INVALID_SEMVER: '{contract.semantic_version}' does not match X.Y.Z"

        if not contract.inputs:
            return False, "EMPTY_INPUTS: Skill must declare at least one input parameter"

        if not contract.outputs:
            return False, "EMPTY_OUTPUTS: Skill must declare at least one output field"

        return True, "Contract integrity verified"

    @classmethod
    def verify_host_runtime_compatibility(
        cls, contract: PortableSkillContract, available_host_tools: Set[str]
    ) -> Tuple[bool, str]:
        missing = contract.required_host_tools - available_host_tools
        if missing:
            return False, f"HOST_INCOMPATIBLE: Host lacks required tools: {sorted(list(missing))}"
        return True, "Host environment satisfies skill contract dependencies"

    @classmethod
    def validate_invocation_payload(
        cls, contract: PortableSkillContract, payload: Dict[str, Any]
    ) -> Tuple[bool, str]:
        for inp in contract.inputs:
            if inp.required and inp.parameter_name not in payload:
                return False, f"MISSING_REQUIRED_INPUT: '{inp.parameter_name}' is required"
        return True, "Payload valid under skill input contract"


def test_portable_skill_contract() -> None:
    # 1. Define portable Citation Audit contract
    contract = PortableSkillContract(
        skill_name="citation_audit",
        semantic_version="1.3.0",
        target_framework_adapter="universal_mcp_agent",
        required_host_tools={"read_excerpt", "semantic_search"},
        inputs=[
            SkillInputContract("claim_text", "str", required=True, description="Claim to check"),
            SkillInputContract("source_doc_id", "str", required=True, description="Document ID"),
            SkillInputContract("min_confidence", "float", required=False, description="Threshold"),
        ],
        outputs=[
            SkillOutputContract("verdict", "str", description="Supported, Refuted, or Unverified"),
            SkillOutputContract("supporting_spans", "list", description="Matching text excerpts"),
        ],
    )

    # 2. Check contract integrity
    ok_int, msg_int = SkillContractValidator.validate_contract_integrity(contract)
    assert ok_int is True

    # 3. Host environment with both tools
    host_capabilities = {"read_excerpt", "semantic_search", "web_browser"}
    ok_compat, msg_compat = SkillContractValidator.verify_host_runtime_compatibility(
        contract, host_capabilities
    )
    assert ok_compat is True
    assert "satisfies" in msg_compat

    # 4. Valid payload
    valid_payload = {"claim_text": "Revenue grew by 15%", "source_doc_id": "10k_annual_2024.pdf"}
    ok_pay, _ = SkillContractValidator.validate_invocation_payload(contract, valid_payload)
    assert ok_pay is True

    # 5. Invalid payload missing required input
    invalid_payload = {"source_doc_id": "10k_annual_2024.pdf"}
    ok_pay_bad, msg_pay_bad = SkillContractValidator.validate_invocation_payload(
        contract, invalid_payload
    )
    assert ok_pay_bad is False
    assert "MISSING_REQUIRED_INPUT" in msg_pay_bad
    assert "claim_text" in msg_pay_bad

    print(
        f"Portable skill contract validator verified: semver={contract.semantic_version}, "
        f"host_compatible=True, input_validation_passed=True"
    )


if __name__ == "__main__":
    test_portable_skill_contract()
