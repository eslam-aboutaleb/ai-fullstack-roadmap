"""Progressive Skill Disclosure: Multi-Tier Dynamic Context Loading.

Demonstrates the 3-tier progressive disclosure pattern for agent skills:
Tier 1: Lightweight metadata index in system prompt for zero-bloat discovery.
Tier 2: Full SKILL.md procedural workflow loaded on-demand when matched.
Tier 3: Specialized schemas and scripts loaded lazily only when referenced.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set


@dataclass(frozen=True)
class SkillMetadataIndex:
    skill_id: str
    name: str
    trigger_intent: str
    short_description: str
    estimated_prompt_tokens: int  # ~30 tokens


@dataclass
class LoadedSkillContext:
    skill_id: str
    procedural_instructions: str
    loaded_resources: Dict[str, str] = field(default_factory=dict)
    active_token_cost: int = 0


class ProgressiveDisclosureEngine:
    """Manages multi-tier dynamic loading to prevent prompt bloat and skill sprawl."""

    def __init__(self) -> None:
        self.catalog: Dict[str, SkillMetadataIndex] = {}
        self.skill_store: Dict[str, Dict[str, Any]] = {}
        self.active_context: Optional[LoadedSkillContext] = None

    def register_skill_package(
        self,
        metadata: SkillMetadataIndex,
        skill_md_content: str,
        resources: Dict[str, str],
    ) -> None:
        self.catalog[metadata.skill_id] = metadata
        self.skill_store[metadata.skill_id] = {
            "instructions": skill_md_content,
            "resources": resources,
            "md_tokens": len(skill_md_content.split()),
        }

    def render_system_prompt_catalog(self) -> str:
        """Tier 1: Minimalist metadata catalog embedded in the base agent prompt."""
        lines = ["Available Specialized Skills:"]
        for s in self.catalog.values():
            lines.append(f"- {s.name} ({s.skill_id}): {s.short_description} [Triggers on: {s.trigger_intent}]")
        return "\n".join(lines)

    def route_and_load_tier2(self, user_intent: str) -> Optional[LoadedSkillContext]:
        """Tier 2: Matches intent and loads the specific SKILL.md into active context."""
        matched_id = None
        for skill_id, meta in self.catalog.items():
            if meta.trigger_intent in user_intent.lower():
                matched_id = skill_id
                break

        if not matched_id:
            self.active_context = None
            return None

        pkg = self.skill_store[matched_id]
        loaded = LoadedSkillContext(
            skill_id=matched_id,
            procedural_instructions=pkg["instructions"],
            active_token_cost=pkg["md_tokens"],
        )
        self.active_context = loaded
        return loaded

    def load_tier3_resource(self, resource_name: str) -> Optional[str]:
        """Tier 3: Lazily loads a supporting schema or reference guide only when requested."""
        if not self.active_context:
            return None
        pkg = self.skill_store[self.active_context.skill_id]
        if resource_name in pkg["resources"]:
            content = pkg["resources"][resource_name]
            self.active_context.loaded_resources[resource_name] = content
            self.active_context.active_token_cost += len(content.split())
            return content
        return None


def test_progressive_disclosure() -> None:
    engine = ProgressiveDisclosureEngine()

    # Register Skill 1: Citation Audit
    engine.register_skill_package(
        metadata=SkillMetadataIndex(
            skill_id="skill_citation_audit",
            name="Citation Audit",
            trigger_intent="audit citations",
            short_description="Verifies statements against source span excerpts.",
            estimated_prompt_tokens=25,
        ),
        skill_md_content="# Citation Audit Procedure\n1. Extract claims.\n2. Fetch spans.\n3. Compare polarity.",
        resources={"rubric.json": '{"threshold": 0.85, "require_exact_quote": true}'},
    )

    # Register Skill 2: Invoice Parse (large enterprise skill with 1000 tokens of rules)
    engine.register_skill_package(
        metadata=SkillMetadataIndex(
            skill_id="skill_invoice_parse",
            name="Invoice Parser",
            trigger_intent="parse invoice",
            short_description="Extracts line items, tax IDs, and vendor billing totals.",
            estimated_prompt_tokens=30,
        ),
        skill_md_content="# Invoice Parsing Manual\nComprehensive enterprise VAT rules... (1500 words)",
        resources={"vat_rates.json": '{"US": 0.08, "UK": 0.20, "DE": 0.19}'},
    )

    # Step 1: Base prompt contains only Tier 1 metadata
    tier1_prompt = engine.render_system_prompt_catalog()
    assert "Citation Audit" in tier1_prompt
    assert "Invoice Parser" in tier1_prompt
    assert "Comprehensive enterprise VAT rules" not in tier1_prompt  # Unused rules NOT in context!

    # Step 2: User asks to audit citations
    loaded = engine.route_and_load_tier2(user_intent="Please audit citations for this answer")
    assert loaded is not None
    assert loaded.skill_id == "skill_citation_audit"
    assert "Extract claims" in loaded.procedural_instructions
    assert "rubric.json" not in loaded.loaded_resources  # Tier 3 not loaded yet!

    # Step 3: During execution, skill explicitly references rubric.json (Tier 3)
    rubric_content = engine.load_tier3_resource("rubric.json")
    assert rubric_content is not None
    assert "threshold" in rubric_content
    assert "rubric.json" in loaded.loaded_resources

    # Invariant: Invoice parsing rules were NEVER loaded into context
    assert "skill_invoice_parse" not in (loaded.skill_id)

    print(
        f"Progressive skill disclosure verified: catalog_skills=2, "
        f"tier1_discovery_rendered=True, tier2_loaded='{loaded.skill_id}', "
        f"tier3_lazy_loaded='rubric.json'"
    )


if __name__ == "__main__":
    test_progressive_disclosure()

