"""Semantic Readiness Pre-Traffic Verifier & Generation Guard.

Demonstrates why basic HTTP 200 liveness checks fail to guarantee production safety.
Verifies semantic readiness: checking data index generation fingerprints, database
schema migration versions, and synthetic query warmup latencies before routing traffic.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class TrafficAdmissionStatus(str, Enum):
    ADMITTED = "admitted"
    REJECTED_OBSOLETE_GENERATION = "rejected_obsolete_generation"
    REJECTED_SCHEMA_MISMATCH = "rejected_schema_mismatch"
    REJECTED_COLD_CACHE = "rejected_cold_cache"


@dataclass
class ContainerReplicaHealthProfile:
    replica_id: str
    http_process_liveness_200: bool  # Basic /healthz
    loaded_index_generation: str  # Vector / data index hash
    connected_db_schema_version: int  # Migration version
    warmup_probe_latency_ms: float  # Synthetic warm query latency


@dataclass(frozen=True)
class AuthoritativeClusterTruth:
    expected_index_generation: str
    minimum_db_schema_version: int
    max_warmup_latency_ms: float = 250.0


class SemanticReadinessGatekeeper:
    """Pre-traffic verification gatekeeper evaluating semantic readiness."""

    def __init__(self, cluster_truth: AuthoritativeClusterTruth) -> None:
        self.truth = cluster_truth
        self.admitted_replicas: List[str] = []
        self.rejected_replicas: List[Dict[str, Any]] = []

    def evaluate_traffic_readiness(
        self, replica: ContainerReplicaHealthProfile
    ) -> Tuple[TrafficAdmissionStatus, str]:
        # Precondition 1: Basic HTTP process liveness
        if not replica.http_process_liveness_200:
            return TrafficAdmissionStatus.REJECTED_COLD_CACHE, "HTTP process not responding"

        # Gate 2: Index Generation Fingerprint
        # Catches the exact failure case where replica returns 200 but serves obsolete data generation!
        if replica.loaded_index_generation != self.truth.expected_index_generation:
            reason = (
                f"OBSOLETE_DATA_GENERATION: Replica has '{replica.loaded_index_generation}', "
                f"expected authoritative '{self.truth.expected_index_generation}'."
            )
            self.rejected_replicas.append({"replica_id": replica.replica_id, "reason": reason})
            return TrafficAdmissionStatus.REJECTED_OBSOLETE_GENERATION, reason

        # Gate 3: Database schema version
        if replica.connected_db_schema_version < self.truth.minimum_db_schema_version:
            reason = (
                f"SCHEMA_VERSION_LAG: Replica connected to migration v{replica.connected_db_schema_version}, "
                f"requires minimum v{self.truth.minimum_db_schema_version}."
            )
            self.rejected_replicas.append({"replica_id": replica.replica_id, "reason": reason})
            return TrafficAdmissionStatus.REJECTED_SCHEMA_MISMATCH, reason

        # Gate 4: Synthetic cache warmup probe latency
        if replica.warmup_probe_latency_ms > self.truth.max_warmup_latency_ms:
            reason = (
                f"COLD_CACHE_LATENCY: Warmup probe {replica.warmup_probe_latency_ms}ms "
                f"exceeds {self.truth.max_warmup_latency_ms}ms threshold."
            )
            self.rejected_replicas.append({"replica_id": replica.replica_id, "reason": reason})
            return TrafficAdmissionStatus.REJECTED_COLD_CACHE, reason

        # Replica is semantically ready for production traffic
        self.admitted_replicas.append(replica.replica_id)
        return TrafficAdmissionStatus.ADMITTED, "Replica admitted to production ingress endpoints."


def test_readiness_pre_traffic_verifier() -> None:
    truth = AuthoritativeClusterTruth(
        expected_index_generation="idx_gen_2026_v2",
        minimum_db_schema_version=42,
        max_warmup_latency_ms=250.0,
    )
    gatekeeper = SemanticReadinessGatekeeper(truth)

    # Replica 1: Process is healthy (HTTP 200), BUT serves the WRONG data generation!
    # (Typical dangerous failure: booted from stale persistent disk or staging config)
    replica_stale_index = ContainerReplicaHealthProfile(
        replica_id="pod_app_stale_gen",
        http_process_liveness_200=True,  # Reports 200 OK!
        loaded_index_generation="idx_gen_2025_v1",  # Obsolete generation!
        connected_db_schema_version=42,
        warmup_probe_latency_ms=85.0,
    )

    status_1, msg_1 = gatekeeper.evaluate_traffic_readiness(replica_stale_index)
    assert status_1 == TrafficAdmissionStatus.REJECTED_OBSOLETE_GENERATION
    assert "OBSOLETE_DATA_GENERATION" in msg_1
    assert "pod_app_stale_gen" not in gatekeeper.admitted_replicas

    # Replica 2: Process healthy and correct index, but schema is un-migrated
    replica_lagging_schema = ContainerReplicaHealthProfile(
        replica_id="pod_app_lagging_schema",
        http_process_liveness_200=True,
        loaded_index_generation="idx_gen_2026_v2",
        connected_db_schema_version=41,  # Lagging schema!
        warmup_probe_latency_ms=90.0,
    )
    status_2, msg_2 = gatekeeper.evaluate_traffic_readiness(replica_lagging_schema)
    assert status_2 == TrafficAdmissionStatus.REJECTED_SCHEMA_MISMATCH

    # Replica 3: Fully verified, semantically ready candidate
    replica_ready = ContainerReplicaHealthProfile(
        replica_id="pod_app_ready_01",
        http_process_liveness_200=True,
        loaded_index_generation="idx_gen_2026_v2",
        connected_db_schema_version=42,
        warmup_probe_latency_ms=110.0,
    )
    status_3, msg_3 = gatekeeper.evaluate_traffic_readiness(replica_ready)
    assert status_3 == TrafficAdmissionStatus.ADMITTED
    assert "pod_app_ready_01" in gatekeeper.admitted_replicas

    print(
        f"Semantic readiness pre-traffic verifier verified: "
        f"obsolete_gen_blocked=True, schema_lag_blocked=True, "
        f"verified_replica_admitted=True, total_rejected={len(gatekeeper.rejected_replicas)}"
    )


if __name__ == "__main__":
    test_readiness_pre_traffic_verifier()

