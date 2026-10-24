"""Indexed lookup vs nested scan computational complexity and key cardinality benchmark.

Demonstrates analyzing algorithmic complexity beyond simple Big-O sloganeering:
1. Nested scan complexity: comparing N incoming records against M candidates without an index
   requires O(N * M) comparisons, causing quadratic latency explosions as data grows.
2. Hash index acceleration: constructing a hash table costs O(M) time and space, followed by
   expected O(1) lookups per record, yielding O(N + M) total complexity.
3. Multi-key cardinality: real-world indexed reconciliation must support duplicate keys
   (one-to-many matches) via bucketed lists, not naive single-value maps.
4. Preprocessing trade-offs: for N=1, building a full index costs O(M) space/time, whereas a
   streaming early-exit scan may be faster.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple


@dataclass(frozen=True)
class IdentityRecord:
    record_id: str
    tax_id: str
    email: str


def nested_loop_reconciliation(
    incoming: List[IdentityRecord], existing: List[IdentityRecord]
) -> Tuple[List[Tuple[str, str]], int]:
    """Naive O(N * M) nested scan: counts exact comparisons performed."""
    matches: List[Tuple[str, str]] = []
    comparison_count = 0

    for inc in incoming:
        for ex in existing:
            comparison_count += 1
            if inc.tax_id == ex.tax_id:
                matches.append((inc.record_id, ex.record_id))

    return matches, comparison_count


def indexed_hash_reconciliation(
    incoming: List[IdentityRecord], existing: List[IdentityRecord]
) -> Tuple[List[Tuple[str, str]], int]:
    """Optimized O(N + M) multi-map index lookup: counts indexing + lookup operations."""
    matches: List[Tuple[str, str]] = []
    operation_count = 0

    # 1. Build phase: O(M) time and space
    index: Dict[str, List[IdentityRecord]] = defaultdict(list)
    for ex in existing:
        operation_count += 1
        index[ex.tax_id].append(ex)

    # 2. Probe phase: O(N) time with O(1) expected hash lookups
    for inc in incoming:
        operation_count += 1
        if inc.tax_id in index:
            for matched_ex in index[inc.tax_id]:
                matches.append((inc.record_id, matched_ex.record_id))

    return matches, operation_count


def run_test_suite() -> None:
    # Existing database with 500 records, including duplicate tax IDs (e.g. joint accounts)
    existing_db: List[IdentityRecord] = []
    for i in range(500):
        # Insert duplicate tax_id for records 10 and 11
        tax_id = "TAX-SHARED-99" if i in (10, 11) else f"TAX-{i}"
        existing_db.append(IdentityRecord(record_id=f"EX-{i}", tax_id=tax_id, email=f"user{i}@corp.com"))

    # Incoming batch of 50 uploaded records to reconcile
    incoming_batch: List[IdentityRecord] = [
        IdentityRecord(record_id=f"INC-{k}", tax_id=f"TAX-{k * 5}", email=f"upload{k}@ext.com")
        for k in range(50)
    ]
    # Add an incoming record matching the duplicate tax ID:
    incoming_batch.append(
        IdentityRecord(record_id="INC-DUPE", tax_id="TAX-SHARED-99", email="dupe@ext.com")
    )

    n = len(incoming_batch)  # 51
    m = len(existing_db)      # 500

    # 1. Execute nested loop scan:
    nested_matches, nested_comps = nested_loop_reconciliation(incoming_batch, existing_db)
    assert nested_comps == n * m  # 51 * 500 = 25,500 comparisons!

    # 2. Execute indexed hash lookup:
    indexed_matches, indexed_ops = indexed_hash_reconciliation(incoming_batch, existing_db)
    # Total ops = 500 (index build) + 51 (probes) = 551 ops:
    assert indexed_ops == n + m
    assert indexed_ops < 600

    # 3. Verify exact outcome parity and duplicate key correctness:
    assert sorted(nested_matches) == sorted(indexed_matches)

    # Verify duplicate tax_id matched both existing records:
    dupe_matches = [m for m in indexed_matches if m[0] == "INC-DUPE"]
    assert len(dupe_matches) == 2
    assert {m[1] for m in dupe_matches} == {"EX-10", "EX-11"}

    # 4. Demonstrate complexity divergence ratio:
    speedup_ratio = nested_comps / indexed_ops
    assert speedup_ratio > 40.0, f"Expected >40x reduction in comparisons, got {speedup_ratio:.1f}x"

    print("All indexed lookup vs nested scan assertions verified successfully.")


if __name__ == "__main__":
    run_test_suite()
