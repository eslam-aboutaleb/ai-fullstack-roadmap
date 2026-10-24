"""Demonstrate instruction-tuned asymmetric task prefixes (query vs passage modes) in dense embeddings."""

class AsymmetricEmbeddingAdapter:
    """
    Asymmetric Embedding Models (e.g. E5, BGE, Instructor) are trained on asymmetric text pairs:
    Queries are short, conversational, and interrogative.
    Documents are long, descriptive, and declarative.
    
    To map both into a unified semantic space, queries require task-specific prefix instructions.
    """
    def __init__(self, query_prefix="Represent this query for retrieving relevant documentation: ", passage_prefix="passage: "):
        self.query_prefix = query_prefix
        self.passage_prefix = passage_prefix

    def format_query(self, raw_query):
        return f"{self.query_prefix}{raw_query.strip()}"

    def format_document(self, raw_document):
        return f"{self.passage_prefix}{raw_document.strip()}"

    def mock_embed(self, formatted_text, is_query):
        # Simulated embedding behavior:
        # If query lacks the required instruction prefix, it embeds in generic sentence space,
        # drifting away from the passage cluster!
        has_proper_prefix = formatted_text.startswith(self.query_prefix) if is_query else formatted_text.startswith(self.passage_prefix)
        if not has_proper_prefix:
            # Semantic drift vector
            return [0.20, 0.40]
        # Aligned coordinate space vector
        return [0.85, 0.52]

adapter = AsymmetricEmbeddingAdapter()

query_text = "How to configure PostgreSQL connection pooling?"
doc_text = "Connection pooling in PostgreSQL is managed via PgBouncer or pool_size in SQLAlchemy."

# Proper formatting:
query_input = adapter.format_query(query_text)
doc_input = adapter.format_document(doc_text)

assert query_input.startswith("Represent this query")
assert doc_input.startswith("passage: ")

vec_query = adapter.mock_embed(query_input, is_query=True)
vec_doc = adapter.mock_embed(doc_input, is_query=False)

# Cosine alignment when both use proper asymmetric prefixes:
dot_aligned = sum(a * b for a, b in zip(vec_query, vec_doc))

# Flawed symmetric case (omitting query instruction):
vec_flawed = adapter.mock_embed(query_text, is_query=True)
dot_unaligned = sum(a * b for a, b in zip(vec_flawed, vec_doc))

assert dot_aligned > dot_unaligned
print(f"Asymmetric task prefix verified: aligned_similarity={round(dot_aligned, 4)}, unaligned_drift={round(dot_unaligned, 4)}")

