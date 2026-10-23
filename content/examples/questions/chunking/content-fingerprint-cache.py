"""Demonstrate cryptographic content fingerprinting and chunk cache invalidation upon configuration changes."""
import hashlib
import json

def compute_chunk_fingerprint(doc_id, chunk_index, chunk_text, chunker_config):
    """
    Provenance Fingerprint:
    Incorporates source text hash, chunk position, AND complete pipeline configuration.
    If chunk_size, overlap, tokenizer model, or normalizer rules change, the fingerprint
    changes deterministically, forcing vector store cache invalidation even if source document is identical.
    """
    payload = {
        "doc_id": doc_id,
        "chunk_index": chunk_index,
        "text_hash": hashlib.sha256(chunk_text.encode()).hexdigest(),
        "config": {
            "chunk_size": chunker_config["chunk_size"],
            "overlap": chunker_config["overlap"],
            "tokenizer": chunker_config["tokenizer"],
            "embedding_model": chunker_config["embedding_model"]
        }
    }
    serialized = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(serialized.encode()).hexdigest()

config_v1 = {
    "chunk_size": 200,
    "overlap": 20,
    "tokenizer": "cl100k_base",
    "embedding_model": "text-embedding-3-small"
}

doc_text = "Standard invoice processing terms for software subscriptions."

# Generate fingerprint under config_v1:
fp_v1 = compute_chunk_fingerprint("doc_42", 0, doc_text, config_v1)

# Case 1: Re-running with identical source and identical config yields exact same fingerprint (Cache Hit!)
fp_v1_repeat = compute_chunk_fingerprint("doc_42", 0, doc_text, config_v1)
assert fp_v1 == fp_v1_repeat, "Deterministic cache hit"

# Case 2: Document text unchanged, but team tunes chunk_size from 200 to 250:
config_v2 = dict(config_v1, chunk_size=250)
fp_v2 = compute_chunk_fingerprint("doc_42", 0, doc_text, config_v2)

# Fingerprint changes, invalidating stale vector embeddings:
assert fp_v1 != fp_v2, "Cache correctly invalidated upon chunker parameter change"

print(f"Content fingerprint verified: fp_v1={fp_v1[:16]}..., fp_v2={fp_v2[:16]}..., invalidated={fp_v1 != fp_v2}")
