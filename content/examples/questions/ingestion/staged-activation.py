"""Demonstrate the distinct phases of ingestion: preparation, validation, and staged atomic activation."""

class IngestionPipeline:
    def __init__(self):
        self.active_collection = "kb_v1"
        self.collections = {
            "kb_v1": ["doc_chunk_1", "doc_chunk_2"],
            "kb_v2_staging": []
        }

    def phase_1_extract_and_chunk(self, raw_documents):
        """Extract text and produce structural chunks with metadata."""
        chunks = []
        for doc in raw_documents:
            # Simulate parsing document and producing chunks
            chunks.append(f"{doc['id']}_chunk_1")
            chunks.append(f"{doc['id']}_chunk_2")
        return chunks

    def phase_2_embed_and_stage(self, chunks):
        """Write embeddings into isolated staging collection without affecting active traffic."""
        for chunk in chunks:
            self.collections["kb_v2_staging"].append(chunk)

    def phase_3_validate_staging(self):
        """Run automated evaluation checks against staging collection before publishing."""
        count = len(self.collections["kb_v2_staging"])
        if count == 0:
            raise ValueError("Validation failed: empty staging collection")
        return True

    def phase_4_atomic_activation(self):
        """Atomically switch active collection pointer once validation passes."""
        self.active_collection = "kb_v2_staging"

pipeline = IngestionPipeline()
raw_docs = [{"id": "policy_2026", "text": "Annual compliance guidelines"}]

# Run phases:
chunks = pipeline.phase_1_extract_and_chunk(raw_docs)
pipeline.phase_2_embed_and_stage(chunks)
assert pipeline.active_collection == "kb_v1", "Traffic continues to use v1 during staging"

pipeline.phase_3_validate_staging()
pipeline.phase_4_atomic_activation()

assert pipeline.active_collection == "kb_v2_staging", "Active collection switched"
print(f"Staged activation complete: active_collection={pipeline.active_collection}, items={len(pipeline.collections['kb_v2_staging'])}")

