"""Demonstrate deterministic chunk ID generation for idempotent upserts and citation reproducibility."""
import uuid
import hashlib

def generate_deterministic_chunk_id(document_id, chunk_index, chunk_text):
    """
    Generate RFC 4122 UUIDv5 scoped to a stable document namespace.
    Ensures that re-chunking an unmodified document yields 100% identical chunk IDs,
    enabling idempotent upserts (INSERT ... ON CONFLICT DO NOTHING / UPDATE)
    without generating orphan duplicate records in the vector database.
    """
    # Deterministic document namespace UUID
    doc_namespace = uuid.uuid5(uuid.NAMESPACE_DNS, f"doc:{document_id}")
    
    # Hash chunk text to catch content modifications
    text_digest = hashlib.sha256(chunk_text.encode()).hexdigest()[:16]
    name = f"{chunk_index}:{text_digest}"
    
    return str(uuid.uuid5(doc_namespace, name))

doc_id = "legal_tos_2026"
text_p1 = "Refunds are processed within 14 business days of return receipt."
text_p2 = "Shipping fees are non-refundable unless items arrived damaged."

id_1a = generate_deterministic_chunk_id(doc_id, 0, text_p1)
id_2a = generate_deterministic_chunk_id(doc_id, 1, text_p2)

# Idempotency Test: Generating IDs again during a pipeline rerun produces identical UUIDs:
id_1b = generate_deterministic_chunk_id(doc_id, 0, text_p1)
id_2b = generate_deterministic_chunk_id(doc_id, 1, text_p2)

assert id_1a == id_1b, "Chunk ID is deterministic across pipeline runs"
assert id_2a == id_2b
assert id_1a != id_2a, "Distinct chunks within document have distinct IDs"

# If text changes, ID updates deterministically:
id_1_mutated = generate_deterministic_chunk_id(doc_id, 0, text_p1 + " Extra policy.")
assert id_1a != id_1_mutated

print(f"Deterministic chunk IDs verified: chunk_0={id_1a}, chunk_1={id_2a}, idempotent={id_1a == id_1b}")
