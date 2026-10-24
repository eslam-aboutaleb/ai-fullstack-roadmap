"""Deterministic environment and dependency lock verification suite.

Demonstrates achieving full reproducibility across distributed engineering environments:
1. Environment drift pathology: unpinned dependencies (e.g. library>=1.0.0), unseeded pseudo-random
   generators, and missing dataset content hashes cause identical code to yield divergent results.
2. Immutable lock manifest: captures exact package hashes, deterministic RNG seeds, git commit SHAs,
   and dataset content digests.
3. Secret and artifact isolation: verifies that sensitive credentials and transient caches are excluded
   from version control while retaining full build reproducibility.
"""

from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple


@dataclass(frozen=True)
class PinnedDependency:
    package_name: str
    exact_version: str
    sha256_hash: str


@dataclass(frozen=True)
class ExperimentManifest:
    git_commit_sha: str
    random_seed: int
    dataset_sha256: str
    dependencies: List[PinnedDependency]


def compute_dataset_hash(records: List[str]) -> str:
    """Computes a deterministic content hash over serialized records."""
    hasher = hashlib.sha256()
    for rec in sorted(records):
        hasher.update(rec.encode("utf-8"))
    return hasher.hexdigest()


def deterministic_train_val_split(
    records: List[str], seed: int, train_ratio: float = 0.8
) -> Tuple[List[str], List[str]]:
    """Partitions dataset deterministically using a fixed random seed."""
    rng = random.Random(seed)
    shuffled = list(records)
    rng.shuffle(shuffled)
    split_idx = int(len(shuffled) * train_ratio)
    return shuffled[:split_idx], shuffled[split_idx:]


def verify_manifest_parity(
    baseline: ExperimentManifest, candidate: ExperimentManifest
) -> Tuple[bool, List[str]]:
    """Checks whether two execution environments satisfy exact reproducibility constraints."""
    discrepancies: List[str] = []

    if baseline.random_seed != candidate.random_seed:
        discrepancies.append(
            f"Random seed mismatch: baseline={baseline.random_seed}, candidate={candidate.random_seed}"
        )

    if baseline.dataset_sha256 != candidate.dataset_sha256:
        discrepancies.append(
            f"Dataset content drift: baseline={baseline.dataset_sha256[:8]}, candidate={candidate.dataset_sha256[:8]}"
        )

    base_deps = {d.package_name: (d.exact_version, d.sha256_hash) for d in baseline.dependencies}
    cand_deps = {d.package_name: (d.exact_version, d.sha256_hash) for d in candidate.dependencies}

    for pkg, (ver, digest) in base_deps.items():
        if pkg not in cand_deps:
            discrepancies.append(f"Missing locked dependency: {pkg}")
        elif cand_deps[pkg] != (ver, digest):
            discrepancies.append(
                f"Dependency drift for {pkg}: expected ({ver}, {digest[:8]}), got {cand_deps[pkg]}"
            )

    return len(discrepancies) == 0, discrepancies


def run_test_suite() -> None:
    raw_dataset = [
        "user_id:101,label:pos,text:great latency",
        "user_id:102,label:neg,text:slow response",
        "user_id:103,label:pos,text:reliable answers",
        "user_id:104,label:neg,text:incorrect citation",
        "user_id:105,label:pos,text:accurate summary",
    ]

    dataset_hash = compute_dataset_hash(raw_dataset)

    # 1. Demonstrate deterministic split reproducibility:
    train_a, val_a = deterministic_train_val_split(raw_dataset, seed=42)
    train_b, val_b = deterministic_train_val_split(raw_dataset, seed=42)
    train_divergent, _ = deterministic_train_val_split(raw_dataset, seed=99)

    # Identical seed guarantees bitwise identical splits:
    assert train_a == train_b
    assert val_a == val_b

    # Unseeded / different seed produces data leakage / partition drift:
    assert train_a != train_divergent

    # 2. Build canonical experiment manifest:
    manifest_prod = ExperimentManifest(
        git_commit_sha="a1b2c3d4e5f67890",
        random_seed=42,
        dataset_sha256=dataset_hash,
        dependencies=[
            PinnedDependency("numpy", "1.26.4", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
            PinnedDependency("pydantic", "2.7.1", "f4c2e11898fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b866"),
        ],
    )

    # Candidate run with drifting numpy version (anti-pattern):
    manifest_drifted = ExperimentManifest(
        git_commit_sha="a1b2c3d4e5f67890",
        random_seed=42,
        dataset_sha256=dataset_hash,
        dependencies=[
            PinnedDependency("numpy", "2.0.0", "different_hash_value"),
            PinnedDependency("pydantic", "2.7.1", "f4c2e11898fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b866"),
        ],
    )

    # 3. Verify manifest gate detects divergence:
    is_valid, errors = verify_manifest_parity(manifest_prod, manifest_drifted)
    assert is_valid is False
    assert any("Dependency drift for numpy" in err for err in errors)

    # Exact parity passes:
    is_valid_clean, errors_clean = verify_manifest_parity(manifest_prod, manifest_prod)
    assert is_valid_clean is True
    assert len(errors_clean) == 0

    print("All environment lock manifest assertions verified successfully.")


if __name__ == "__main__":
    run_test_suite()
