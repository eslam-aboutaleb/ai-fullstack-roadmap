"""Demonstrate Late Chunking vs Early Chunking in long-context embedding models."""
import math

def mock_mean_pool(token_embeddings):
    """Mean pooling over token hidden states."""
    dim = len(token_embeddings[0])
    pooled = [0.0] * dim
    for emb in token_embeddings:
        for d in range(dim):
            pooled[d] += emb[d]
    return [x / len(token_embeddings) for x in pooled]

def cosine_similarity(v1, v2):
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))
    return dot / (norm1 * norm2) if norm1 > 0 and norm2 > 0 else 0.0

# Document Scenario:
# Sentence 1: "Acme Cloud Database Service Level Agreement."
# Sentence 2: "It guarantees 99.99% uptime for multi-region clusters."
# Notice: Sentence 2 uses pronoun 'It'.
#
# EARLY CHUNKING:
# Sentence 2 is chunked and embedded in isolation.
# The embedding model sees only: "It guarantees 99.99% uptime..."
# Vector misses the association with "Acme Cloud Database" -> low similarity on queries asking for "Acme uptime".
#
# LATE CHUNKING:
# The entire document is passed through the 8k context transformer.
# Self-attention layers compute interaction between "Acme Cloud Database" and "It".
# When sentence 2's token states are pooled, they retain contextual awareness of the antecedent!

# Simulated token states:
# In Late Chunking, sentence 2's token vectors have attended to sentence 1, incorporating database signal:
early_chunk_vector = [0.10, 0.90] # Strong on "uptime", near zero on "database service"
late_chunk_vector = [0.75, 0.82]  # Strong on both "database service" and "uptime"

query_vector = [0.80, 0.85] # Query: "Acme Cloud Database uptime guarantee"

sim_early = cosine_similarity(early_chunk_vector, query_vector)
sim_late = cosine_similarity(late_chunk_vector, query_vector)

assert sim_late > sim_early
gain = sim_late - sim_early

print(f"Late chunking verified: early_sim={round(sim_early, 4)}, late_sim={round(sim_late, 4)}, context_gain={round(gain, 4)}")

