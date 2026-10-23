"""Demonstrate Hierarchical Parent-Child chunking: small child for vector search, large parent for LLM context."""

class HierarchicalStore:
    def __init__(self):
        self.parents = {} # parent_id -> full context text
        self.children = [] # list of {child_id, parent_id, vector_embedding, text}

    def index_document(self, parent_id, parent_text, child_passages, mock_child_embeddings):
        self.parents[parent_id] = parent_text
        for i, (child_text, emb) in enumerate(zip(child_passages, mock_child_embeddings)):
            self.children.append({
                "child_id": f"{parent_id}_c{i}",
                "parent_id": parent_id,
                "text": child_text,
                "embedding": emb
            })

    def search_and_expand_to_parent(self, query_vector):
        """
        1. Search small child passages for precise vector similarity.
        2. Resolve parent_id from best matching child.
        3. Return parent context to the generation prompt, providing full surrounding clauses.
        """
        # Find best matching child (dot product similarity):
        best_child = max(self.children, key=lambda c: sum(a * b for a, b in zip(c["embedding"], query_vector)))
        
        # Expand to complete parent document:
        parent_context = self.parents[best_child["parent_id"]]
        return {
            "matched_child_id": best_child["child_id"],
            "matched_passage": best_child["text"],
            "expanded_parent_context": parent_context
        }

store = HierarchicalStore()

# Parent: Full 400-word SLA contract section containing definitions, metrics, and credit policies
full_sla_policy = (
    "SLA TERMS: Acme Cloud guarantees 99.99% monthly availability for multi-zone deployments. "
    "EXCLUSIONS: Scheduled maintenance windows announced 48 hours in advance are excluded. "
    "CREDIT REMEDY: Customers experiencing availability between 99.0% and 99.9% are entitled "
    "to a 10% billing credit upon submitting a claim within 30 days of the incident."
)

child_passages = [
    "Acme Cloud guarantees 99.99% monthly availability for multi-zone deployments.",
    "Customers experiencing availability between 99.0% and 99.9% receive a 10% billing credit."
]
mock_embs = [[0.95, 0.10], [0.15, 0.92]]

store.index_document("sla_section_4", full_sla_policy, child_passages, mock_embs)

# Query specifically asks about compensation/credit:
query_vec = [0.12, 0.95]
result = store.search_and_expand_to_parent(query_vec)

assert result["matched_child_id"] == "sla_section_4_c1"
# Verify that the generation prompt receives the parent context with both rule AND exclusions:
assert "99.99% monthly availability" in result["expanded_parent_context"]
assert "EXCLUSIONS:" in result["expanded_parent_context"]

print(f"Parent-child retrieval verified: matched_child={result['matched_child_id']}, parent_length={len(result['expanded_parent_context'])} chars")
