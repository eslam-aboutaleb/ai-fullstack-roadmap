"""Production Delivery Gates & Immutable Artifact Promotion.

Evaluates an immutable container artifact against strict production delivery gates:
cryptographic provenance signing, vulnerability thresholds, externalized secret isolation,
database schema backward-compatibility, and automated rollback dry-run verification.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass(frozen=True)
class ContainerArtifactRecord:
    git_commit_sha: str
    image_digest: str
    signature_verified: bool
    critical_cve_count: int
    baked_secrets_found: bool
    schema_compatible: bool
    rollback_rehearsal_verified: bool


class ProductionDeliveryGatekeeper:
    """Enforces non-negotiable quality and security gates for artifact promotion."""

    def __init__(self, allowed_max_critical_cves: int = 0) -> None:
        self.allowed_max_critical_cves = allowed_max_critical_cves
        self.promotion_audit_log: List[str] = []

    def evaluate_artifact_promotion(
        self, artifact: ContainerArtifactRecord
    ) -> Tuple[bool, List[str]]:
        rejections: List[str] = []

        # Gate 1: Cryptographic provenance
        if not artifact.signature_verified:
            rejections.append("PROVENANCE_FAILED: Container image digest signature could not be verified.")

        # Gate 2: Security vulnerability scan
        if artifact.critical_cve_count > self.allowed_max_critical_cves:
            rejections.append(
                f"CVE_THRESHOLD_EXCEEDED: Artifact contains {artifact.critical_cve_count} critical CVEs "
                f"(max allowed: {self.allowed_max_critical_cves})."
            )

        # Gate 3: Secret isolation
        if artifact.baked_secrets_found:
            rejections.append("SECRET_LEAK_DETECTED: Static secrets or credentials found baked into image layers.")

        # Gate 4: Database schema compatibility
        if not artifact.schema_compatible:
            rejections.append("SCHEMA_INCOMPATIBLE: Artifact requires uncommitted or backward-incompatible DB schema.")

        # Gate 5: Verified rollback path
        if not artifact.rollback_rehearsal_verified:
            rejections.append("ROLLBACK_UNVERIFIED: Rollback recovery drill has not been verified in staging.")

        is_promoted = len(rejections) == 0
        if is_promoted:
            self.promotion_audit_log.append(f"PROMOTED: Image {artifact.image_digest[:16]} to production.")
        else:
            self.promotion_audit_log.append(
                f"REJECTED: Image {artifact.image_digest[:16]} failed {len(rejections)} gates."
            )

        return is_promoted, rejections


def test_delivery_gates() -> None:
    gatekeeper = ProductionDeliveryGatekeeper()

    # 1. Unsafe Candidate: Missing rollback rehearsal and baked secrets!
    unsafe_artifact = ContainerArtifactRecord(
        git_commit_sha="a7f8e91c2b3d4e5f",
        image_digest="sha256:4b35e21970b12ad3e7b8f9e1c2d3a4b5c6d7e8f9",
        signature_verified=True,
        critical_cve_count=0,
        baked_secrets_found=True,  # Fails!
        schema_compatible=True,
        rollback_rehearsal_verified=False,  # Fails!
    )

    is_promoted_unsafe, reasons_unsafe = gatekeeper.evaluate_artifact_promotion(unsafe_artifact)
    assert is_promoted_unsafe is False
    assert len(reasons_unsafe) == 2
    assert any("SECRET_LEAK_DETECTED" in r for r in reasons_unsafe)
    assert any("ROLLBACK_UNVERIFIED" in r for r in reasons_unsafe)

    # 2. Production-Grade Ready Artifact
    clean_artifact = ContainerArtifactRecord(
        git_commit_sha="b8e9f02d3c4e5a6b",
        image_digest="sha256:7c46f32081c23be4f8c9a0f2d3e4b5c6d7e8f9a0",
        signature_verified=True,
        critical_cve_count=0,
        baked_secrets_found=False,
        schema_compatible=True,
        rollback_rehearsal_verified=True,
    )

    is_promoted_clean, reasons_clean = gatekeeper.evaluate_artifact_promotion(clean_artifact)
    assert is_promoted_clean is True
    assert len(reasons_clean) == 0
    assert len(gatekeeper.promotion_audit_log) == 2

    print(
        f"Production delivery gates verified: unsafe_promoted={is_promoted_unsafe}, "
        f"clean_promoted={is_promoted_clean}, "
        f"gates_evaluated=5"
    )


if __name__ == "__main__":
    test_delivery_gates()
