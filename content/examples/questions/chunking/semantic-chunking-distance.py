"""Implement Semantic Chunking using embedding cosine distance variance across sentences."""
import math

def cosine_similarity(v1, v2):
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))
    return dot / (norm1 * norm2) if norm1 > 0 and norm2 > 0 else 0.0

def semantic_chunking(sentences, mock_embeddings, threshold_percentile=75):
    """
    Calculate semantic distance between consecutive sentences: d_i = 1 - cos(e_i, e_{i+1}).
    Split at local distance spikes that exceed the statistical percentile threshold.
    """
    distances = []
    for i in range(len(sentences) - 1):
        sim = cosine_similarity(mock_embeddings[i], mock_embeddings[i + 1])
        distances.append(1.0 - sim)

    # Calculate threshold value
    sorted_dists = sorted(distances)
    idx = int(len(sorted_dists) * (threshold_percentile / 100.0))
    split_threshold = sorted_dists[min(idx, len(sorted_dists) - 1)]

    chunks = []
    current_chunk = [sentences[0]]

    for i, dist in enumerate(distances):
        if dist >= split_threshold:
            # Significant topic transition detected!
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentences[i + 1]]
        else:
            current_chunk.append(sentences[i + 1])

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks, distances, split_threshold

# 4 sentences: Sentences 0 and 1 belong to Topic A (Database locks);
# Sentences 2 and 3 belong to Topic B (Frontend CSS layout).
sentences = [
    "PostgreSQL uses row-level locks for concurrent transactional updates.",
    "The SELECT FOR UPDATE statement blocks conflicting writers on the target tuple.",
    "CSS Flexbox provides flexible one-dimensional box alignment across viewport widths.",
    "The justify-content property distributes free space along the main axis."
]

# Simulated sentence embeddings (2D vectors)
mock_embeddings = [
    [0.98, 0.05], # Topic A sentence 0
    [0.95, 0.08], # Topic A sentence 1
    [0.05, 0.96], # Topic B sentence 2 (orthogonal vector)
    [0.08, 0.94]  # Topic B sentence 3
]

chunks, dists, threshold = semantic_chunking(sentences, mock_embeddings)

# A distance spike occurs between sentence 1 (Topic A) and sentence 2 (Topic B):
# Topic A distance: ~0.001; Topic B distance: ~0.001; Transition distance: ~0.99
assert len(chunks) == 2, f"Expected 2 semantic chunks, got {len(chunks)}"
assert "PostgreSQL" in chunks[0] and "SELECT FOR UPDATE" in chunks[0]
assert "CSS Flexbox" in chunks[1] and "justify-content" in chunks[1]

print(f"Semantic chunking verified: chunk_count={len(chunks)}, transition_distance={round(dists[1], 4)}, threshold={round(threshold, 4)}")
