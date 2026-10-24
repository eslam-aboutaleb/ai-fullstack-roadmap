"""Implement token-aware sliding window chunking with strict stride invariants and citation offsets."""

def sliding_window_chunker(token_list, chunk_size, chunk_overlap):
    """
    Invariants:
      1. chunk_size must be positive (> 0).
      2. chunk_overlap must be non-negative (>= 0).
      3. chunk_overlap MUST be strictly less than chunk_size (overlap < chunk_size)
         to guarantee forward progress (stride > 0). If overlap >= chunk_size, the chunker
         enters an infinite loop or negative indexing!
    """
    if chunk_size <= 0:
        raise ValueError(f"chunk_size must be > 0, got {chunk_size}")
    if not (0 <= chunk_overlap < chunk_size):
        raise ValueError(f"chunk_overlap ({chunk_overlap}) must be >= 0 and strictly < chunk_size ({chunk_size})")

    stride = chunk_size - chunk_overlap
    chunks = []
    
    start_idx = 0
    total_tokens = len(token_list)

    while start_idx < total_tokens:
        end_idx = min(start_idx + chunk_size, total_tokens)
        chunk_tokens = token_list[start_idx:end_idx]
        
        chunks.append({
            "chunk_index": len(chunks),
            "tokens": chunk_tokens,
            "token_start": start_idx,
            "token_end": end_idx,
            "stride": stride
        })
        
        if end_idx >= total_tokens:
            break
            
        start_idx += stride

    return chunks

tokens = [f"t{i}" for i in range(1, 13)] # 12 tokens
chunk_size = 5
chunk_overlap = 2 # stride = 3

chunks = sliding_window_chunker(tokens, chunk_size, chunk_overlap)

# Expected chunks with size 5, overlap 2, stride 3:
# Chunk 0: tokens 0 to 5  -> [t1, t2, t3, t4, t5]
# Chunk 1: tokens 3 to 8  -> [t4, t5, t6, t7, t8]  (t4, t5 repeated as overlap context!)
# Chunk 2: tokens 6 to 11 -> [t7, t8, t9, t10, t11]
# Chunk 3: tokens 9 to 12 -> [t10, t11, t12]
assert len(chunks) == 4
assert chunks[0]["tokens"][-2:] == chunks[1]["tokens"][:2], "Overlap tokens matched between chunk 0 and 1"

# Verify invariant rejection:
overlap_rejected = False
try:
    sliding_window_chunker(tokens, chunk_size=5, chunk_overlap=5) # overlap == chunk_size!
except ValueError:
    overlap_rejected = True

assert overlap_rejected is True
print(f"Sliding window verified: total_chunks={len(chunks)}, stride=3, invalid_overlap_rejected={overlap_rejected}")

