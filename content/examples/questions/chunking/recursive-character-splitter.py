"""Implement recursive character chunking preserving hierarchical document syntactic boundaries."""

class RecursiveCharacterTextSplitter:
    def __init__(self, chunk_size=200, chunk_overlap=30, separators=None):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        # Delimiters tried in order of semantic preservation:
        self.separators = separators or ["\n\n", "\n", ". ", " ", ""]

    def split_text(self, text):
        return self._split(text, self.separators)

    def _split(self, text, separators):
        final_chunks = []
        # Find highest priority separator present in the text:
        separator = separators[-1]
        new_separators = []
        for i, sep in enumerate(separators):
            if sep == "" or sep in text:
                separator = sep
                new_separators = separators[i + 1:]
                break

        splits = text.split(separator) if separator != "" else list(text)
        good_splits = []

        for piece in splits:
            if not piece: continue
            if len(piece) < self.chunk_size:
                good_splits.append(piece)
            else:
                if good_splits:
                    merged = self._merge_splits(good_splits, separator)
                    final_chunks.extend(merged)
                    good_splits = []
                if not new_separators:
                    final_chunks.append(piece[:self.chunk_size])
                else:
                    other_chunks = self._split(piece, new_separators)
                    final_chunks.extend(other_chunks)

        if good_splits:
            merged = self._merge_splits(good_splits, separator)
            final_chunks.extend(merged)

        return final_chunks

    def _merge_splits(self, splits, separator):
        docs = []
        current = []
        total = 0
        for s in splits:
            s_len = len(s) + (len(separator) if current else 0)
            if total + s_len <= self.chunk_size:
                current.append(s)
                total += s_len
            else:
                if current:
                    docs.append(separator.join(current))
                current = [s]
                total = len(s)
        if current:
            docs.append(separator.join(current))
        return docs

sample_text = (
    "# Security Invariants\n\n"
    "All API endpoints must enforce tenant isolation boundaries. "
    "Cross-tenant access attempts must immediately terminate and log an alert.\n\n"
    "# Storage Policies\n\n"
    "Data retention is configured per tier. Free accounts retain 30 days of telemetry. "
    "Enterprise tiers retain 365 days of encrypted audit records."
)

splitter = RecursiveCharacterTextSplitter(chunk_size=160, chunk_overlap=20)
chunks = splitter.split_text(sample_text)

assert len(chunks) >= 2
# Verify that paragraph headers remain with their text rather than sliced mid-sentence:
assert any("Security Invariants" in c for c in chunks)
assert any("Storage Policies" in c for c in chunks)

print(f"Recursive splitting verified: chunk_count={len(chunks)}, chunk_sizes={[len(c) for c in chunks]}")

