"""Immutable manifest and lineage auditing for derived vector index builds.

Demonstrates how end-to-end lineage manifests eliminate the 'mutable tag trap':
1. The mutable label trap: tagging indexes as 'prod-latest' prevents engineers from determining
   whether a retrieval recall regression stems from corpus updates, chunking code drift, or embedding model upgrades.
2. Four-vector lineage manifest: cryptographically binds:
   - Source dataset snapshot content hash
   - Pipeline code git commit SHA
   - Model identifier and embedding dimension
   - Index build hyperparameters (e.g. HNSW M and ef_construction)
3. Deterministic generation hashing: generates immutable, content-addressed index generation IDs,
   enabling instantaneous diffing and regression root-cause isolation.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass(frozen=True)
class IndexBuildManifest:
    source_snapshot_hash: str
    pipeline_git_sha: str
    embedding_model_id: str
    embedding_dim: int
    index_params: Dict[str, Any]

    def compute_generation_id(self) -> str:
        """Derives a deterministic, content-addressed generation identifier."""
        serialized = json.dumps(asdict(self), sort_keys=True)
        digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        return f"GEN-{digest[:16]}"


def isolate_lineage_divergence(
    manifest_a: IndexBuildManifest, manifest_b: IndexBuildManifest
) -> List[str]:
    """Isolates the exact root cause of divergence between two index builds."""
    diffs: List[str] = []

    if manifest_a.source_snapshot_hash != manifest_b.source_snapshot_hash:
        diffs.append("SOURCE_DATA_DRIFT: Raw document corpus snapshot changed")

    if manifest_a.pipeline_git_sha != manifest_b.pipeline_git_sha:
        diffs.append("CODE_LOGIC_DRIFT: Ingestion/chunking pipeline git commit changed")

    if (
        manifest_a.embedding_model_id != manifest_b.embedding_model_id
        or manifest_a.embedding_dim != manifest_b.embedding_dim
    ):
        diffs.append("MODEL_WEIGHTS_DRIFT: Embedding model version or dimensions changed")

    if manifest_a.index_params != manifest_b.index_params:
        diffs.append("INDEX_PARAMS_DRIFT: Index hyperparameters changed")

    return diffs


def run_test_suite() -> None:
    # Baseline index in production:
    manifest_baseline = IndexBuildManifest(
        source_snapshot_hash="hash-corpus-v1-abc",
        pipeline_git_sha="git-commit-111",
        embedding_model_id="embed-v1-frozen",
        embedding_dim=768,
        index_params={"M": 16, "efConstruction": 200, "metric": "cosine"},
    )
    gen_baseline = manifest_baseline.compute_generation_id()

    # Rebuild A: Identical inputs -> Must yield bitwise-identical generation ID
    manifest_rebuild_identical = IndexBuildManifest(
        source_snapshot_hash="hash-corpus-v1-abc",
        pipeline_git_sha="git-commit-111",
        embedding_model_id="embed-v1-frozen",
        embedding_dim=768,
        index_params={"M": 16, "efConstruction": 200, "metric": "cosine"},
    )
    assert manifest_rebuild_identical.compute_generation_id() == gen_baseline

    # Candidate Index B: Suffered retrieval regression.
    # Mystery: Was it data or code?
    manifest_regressed = IndexBuildManifest(
        source_snapshot_hash="hash-corpus-v1-abc",  # Data is unchanged!
        pipeline_git_sha="git-commit-222-refactor",  # Code refactored!
        embedding_model_id="embed-v1-frozen",
        embedding_dim=768,
        index_params={"M": 16, "efConstruction": 200, "metric": "cosine"},
    )
    gen_regressed = manifest_regressed.compute_generation_id()

    # Generation IDs differ:
    assert gen_regressed != gen_baseline

    # Run lineage audit diff:
    divergence_causes = isolate_lineage_divergence(manifest_baseline, manifest_regressed)
    assert len(divergence_causes) == 1
    assert "CODE_LOGIC_DRIFT" in divergence_causes[0]
    assert "SOURCE_DATA_DRIFT" not in str(divergence_causes)

    # Candidate Index C: Model upgrade
    manifest_model_upgrade = IndexBuildManifest(
        source_snapshot_hash="hash-corpus-v1-abc",
        pipeline_git_sha="git-commit-111",
        embedding_model_id="embed-v2-preview",  # Model changed
        embedding_dim=768,
        index_params={"M": 16, "efConstruction": 200, "metric": "cosine"},
    )
    model_diffs = isolate_lineage_divergence(manifest_baseline, manifest_model_upgrade)
    assert any("MODEL_WEIGHTS_DRIFT" in d for d in model_diffs)

    print("All immutable manifest lineage audit assertions verified successfully.")


if __name__ == "__main__":
    run_test_suite()
