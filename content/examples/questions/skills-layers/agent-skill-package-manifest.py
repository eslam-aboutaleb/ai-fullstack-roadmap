"""Agent Skill Package Manifest & Boundary Validation.

Demonstrates the architectural structure of a production-grade agent skill package.
Distinguishes declarative procedural guidance (skills) from executable capabilities
(tools), enforcing dependency validation and credential isolation.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple


class ToolRiskLevel(str, Enum):
    READ_ONLY = "read_only"
    STATE_MUTATION = "state_mutation"
    HIGH_IMPACT = "high_impact"


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    risk_level: ToolRiskLevel
    required_permissions: Set[str]


@dataclass
class SkillPackageManifest:
    name: str
    version: str
    entrypoint: str  # e.g. "SKILL.md"
    description: str
    triggers_when: str
    negative_boundary: str  # When NOT to use
    required_tools: Set[str]
    bundled_resources: List[str] = field(default_factory=list)
    bundled_scripts: List[str] = field(default_factory=list)


class SkillRegistryManager:
    """Manages skill packages, verifying tool dependencies against host capabilities."""

    def __init__(self, available_host_tools: Dict[str, ToolDefinition]) -> None:
        self.host_tools = available_host_tools
        self.registered_skills: Dict[str, SkillPackageManifest] = {}

    def register_skill(self, manifest: SkillPackageManifest) -> Tuple[bool, str]:
        # Pre-flight Check 1: Tool dependencies must be provided by the host environment
        missing_tools = manifest.required_tools - set(self.host_tools.keys())
        if missing_tools:
            return False, f"MISSING_DEPENDENCY: Host lacks required tools: {sorted(list(missing_tools))}"

        # Pre-flight Check 2: Manifest must have explicit negative boundaries to prevent sprawl
        if not manifest.negative_boundary:
            return False, "INVALID_MANIFEST: Skill must declare negative boundary ('when not to use')"

        self.registered_skills[manifest.name] = manifest
        return True, f"Skill '{manifest.name}' v{manifest.version} registered successfully"


def test_skill_package_manifest() -> None:
    # 1. Declare Host Executable Tools (Capabilities)
    host_tools = {
        "read_source_excerpt": ToolDefinition(
            name="read_source_excerpt",
            description="Reads bounded span from document",
            risk_level=ToolRiskLevel.READ_ONLY,
            required_permissions={"doc.read"},
        ),
        "highlight_citation": ToolDefinition(
            name="highlight_citation",
            description="Annotates citation span in document viewer",
            risk_level=ToolRiskLevel.STATE_MUTATION,
            required_permissions={"doc.write"},
        ),
    }

    registry = SkillRegistryManager(host_tools)

    # 2. Package valid Citation Audit Skill
    citation_skill = SkillPackageManifest(
        name="citation_audit",
        version="1.2.0",
        entrypoint="SKILL.md",
        description="Verifies factual claims in generated answers against retrieved source documents",
        triggers_when="When the user requests fact-checking or citation audit of generated answers",
        negative_boundary="Do not use for generating new creative text or general document summarization",
        required_tools={"read_source_excerpt", "highlight_citation"},
        bundled_resources=["resources/rubric.json"],
        bundled_scripts=["scripts/normalize_quotes.py"],
    )

    ok, msg = registry.register_skill(citation_skill)
    assert ok is True
    assert "registered successfully" in msg
    assert "citation_audit" in registry.registered_skills

    # 3. Package incompatible skill requiring missing external tool
    unsupported_skill = SkillPackageManifest(
        name="audio_transcriber",
        version="0.1.0",
        entrypoint="SKILL.md",
        description="Transcribes raw speech audio",
        triggers_when="When audio files are uploaded",
        negative_boundary="Do not use for text processing",
        required_tools={"whisper_transcribe_audio", "read_source_excerpt"},
    )

    ok_bad, msg_bad = registry.register_skill(unsupported_skill)
    assert ok_bad is False
    assert "MISSING_DEPENDENCY" in msg_bad
    assert "whisper_transcribe_audio" in msg_bad

    print(
        f"Agent skill package manifest verified: skill_registered='{citation_skill.name}', "
        f"tools_bound={sorted(list(citation_skill.required_tools))}, "
        f"dependency_check_passed=True"
    )


if __name__ == "__main__":
    test_skill_package_manifest()
