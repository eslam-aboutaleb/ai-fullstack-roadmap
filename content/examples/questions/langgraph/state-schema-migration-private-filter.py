"""State Schema Evolution Across Deployments and Private State Streaming Projection.

Demonstrates:
1. Versioned Checkpoint Schema Migration:
   - Detects legacy v1 checkpoints stored in persistent checkpointer databases.
   - Migrates state to v2 by rehydrating authoritative tenant scope from trusted records and backfilling
     safe defaults without dropping in-flight workflows.
2. Private State Filtering (Safe Streaming Projection):
   - Internal graph state contains private engineering details: raw system prompts, model scratchpads,
     internal node tokens, and database connection metadata.
   - Enforces an allowlist projection before emitting state over public Server-Sent Events (SSE) or WebSockets.
"""

from dataclasses import asdict, dataclass, field
import json
from typing import Any, Dict, List, Optional, Set


# --- 1. Schema Definitions ---
@dataclass
class LegacyV1Checkpoint:
    workflow_id: str
    user_id: str
    query: str
    messages: List[str]
    schema_version: int = 1


@dataclass
class ModernV2State:
    workflow_id: str
    user_id: str
    tenant_scope: str  # Added in v2! Required for isolation
    query: str
    messages: List[str]
    retry_count: int = 0  # Added in v2!
    schema_version: int = 2
    # Private internal fields that must NEVER leak to public streaming!
    internal_scratchpad: Optional[str] = None
    database_conn_uri: Optional[str] = None


class CheckpointMigrationEngine:
    """Migrates serialized checkpoints across application versions."""

    # Mock authoritative tenant directory for rehydrating missing scope
    AUTHORITATIVE_USER_DIRECTORY = {
        "usr_991": "tenant_enterprise_apac",
        "usr_404": "tenant_standard_na"
    }

    @classmethod
    def deserialize_and_migrate(cls, raw_checkpoint: Dict[str, Any]) -> ModernV2State:
        version = raw_checkpoint.get("schema_version", 1)

        if version == 1:
            # Migration v1 -> v2
            user_id = raw_checkpoint["user_id"]
            # Critical invariant: Do NOT invent or hallucinate tenant scope; rehydrate from authoritative DB!
            tenant_scope = cls.AUTHORITATIVE_USER_DIRECTORY.get(user_id, "tenant_quarantine_default")

            return ModernV2State(
                workflow_id=raw_checkpoint["workflow_id"],
                user_id=user_id,
                tenant_scope=tenant_scope,
                query=raw_checkpoint["query"],
                messages=raw_checkpoint.get("messages", []),
                retry_count=0,
                schema_version=2,
                internal_scratchpad=None,
                database_conn_uri="postgres://app_user:masked@prod-cluster/db"
            )

        elif version == 2:
            return ModernV2State(**raw_checkpoint)

        raise ValueError(f"Unsupported schema version: {version}")


class PublicStreamingProjection:
    """Allowlist filter projecting only public fields to external client streams."""

    PUBLIC_ALLOWLIST = {"workflow_id", "status", "public_message", "schema_version"}

    @classmethod
    def project_for_public_client(cls, state: ModernV2State, status: str, public_message: str) -> Dict[str, Any]:
        full_dict = asdict(state)
        full_dict["status"] = status
        full_dict["public_message"] = public_message

        # Allowlist projection: discard private fields (internal_scratchpad, database_conn_uri, tenant_scope)
        projected = {k: v for k, v in full_dict.items() if k in cls.PUBLIC_ALLOWLIST}
        return projected


def main():
    # 1. Test In-Flight V1 Checkpoint Migration
    print("1. Migrating Legacy V1 Checkpoint to Modern V2 Schema:")
    v1_raw_json = {
        "workflow_id": "wf_flight_1001",
        "user_id": "usr_991",
        "query": "Upgrade flight seat to business class",
        "messages": ["User requested upgrade"],
        "schema_version": 1
    }

    migrated_state = CheckpointMigrationEngine.deserialize_and_migrate(v1_raw_json)
    print(f"  Migrated Version: {migrated_state.schema_version}")
    print(f"  Rehydrated Tenant Scope: '{migrated_state.tenant_scope}'")
    print(f"  Backfilled Default retry_count: {migrated_state.retry_count}")

    assert migrated_state.schema_version == 2
    assert migrated_state.tenant_scope == "tenant_enterprise_apac"
    assert migrated_state.retry_count == 0

    # 2. Add private operational state
    migrated_state.internal_scratchpad = "Model reasoning: Candidate has frequent flyer status Tier-1."
    migrated_state.database_conn_uri = "postgres://root:SuperSecretP@ss@prod-db.internal:5432/core"

    # 3. Test Public Streaming Projection (Security & Privacy Filtering)
    print("\n2. Projecting State for Public Streaming Output:")
    public_payload = PublicStreamingProjection.project_for_public_client(
        state=migrated_state,
        status="RUNNING",
        public_message="Processing seat upgrade request..."
    )
    print(f"  Public Payload:\n{json.dumps(public_payload, indent=2)}")

    # Assert that private internal fields were completely stripped!
    assert "internal_scratchpad" not in public_payload
    assert "database_conn_uri" not in public_payload
    assert "SuperSecretP@ss" not in json.dumps(public_payload)
    assert public_payload["workflow_id"] == "wf_flight_1001"
    assert public_payload["status"] == "RUNNING"

    print("\nState schema evolution across deployments and private state filtering verified successfully.")


if __name__ == "__main__":
    main()

