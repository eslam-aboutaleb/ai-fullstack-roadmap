"""Demonstrate evaluating chunk overlap recall without counting duplicate passages as extra evidence."""

# Scenario: Ground-truth answer requires TWO distinct pieces of evidence:
# 1. General Rule (Section A)
# 2. Statutory Exception (Section B)
ground_truth_criteria = {"rule_general", "exception_clause"}

# Top 5 retrieved chunks from vector search with 50% chunk overlap:
# Chunks 1, 2, 3, and 4 all come from Section A (overlapping windows of the same general paragraph).
# Chunk 5 comes from an irrelevant introductory paragraph.
# Section B (statutory exception) was ranked #6 and missed due to candidate truncation!
retrieved_chunks = [
    {"chunk_id": "c1", "source_section": "section_A", "evidence": "rule_general"},
    {"chunk_id": "c2", "source_section": "section_A", "evidence": "rule_general"}, # Overlapping window
    {"chunk_id": "c3", "source_section": "section_A", "evidence": "rule_general"}, # Overlapping window
    {"chunk_id": "c4", "source_section": "section_A", "evidence": "rule_general"}, # Overlapping window
    {"chunk_id": "c5", "source_section": "section_Intro", "evidence": "background"}
]

def evaluate_naive_hit_rate(chunks, target_evidence):
    """
    FLAWED METRIC: Naive hit count.
    Counts 4 hits for 'rule_general' as 4 points of recall,
    giving the false illusion of high retrieval performance (4/5 = 80% precision)!
    """
    hits = [c for c in chunks if c["evidence"] in target_evidence]
    return len(hits)

def evaluate_deduplicated_evidence_recall(chunks, required_criteria):
    """
    RIGOROUS METRIC: Deduplicated evidence coverage.
    Deduplicates overlapping chunks by source passage / section identity before measuring
    how many required criteria were recalled.
    """
    recalled_criteria = set()
    for c in chunks:
        if c["evidence"] in required_criteria:
            recalled_criteria.add(c["evidence"])
            
    coverage_rate = len(recalled_criteria) / len(required_criteria)
    missing_criteria = required_criteria - recalled_criteria
    return coverage_rate, missing_criteria

naive_hits = evaluate_naive_hit_rate(retrieved_chunks, ground_truth_criteria)
coverage, missing = evaluate_deduplicated_evidence_recall(retrieved_chunks, ground_truth_criteria)

# Naive metric reports 4 hits; true criteria coverage is only 50% because the exception was crowded out!
assert naive_hits == 4
assert coverage == 0.50
assert "exception_clause" in missing

print(f"Chunk overlap evaluation verified: naive_hits={naive_hits}/5, true_criteria_coverage={coverage * 100}%, missing={missing}")

