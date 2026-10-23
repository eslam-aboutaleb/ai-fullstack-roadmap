"""Calculate vector database RAM sizing across precision formats (float32, fp16, int8, binary) and HNSW graph overhead."""

def calculate_vector_storage_footprint(num_vectors, dimension, precision="float32", hnsw_m=16, metadata_bytes_per_doc=256):
    """
    Precision bytes per coordinate:
      float32: 4 bytes
      fp16:    2 bytes
      int8:    1 byte (Scalar Quantization)
      binary:  1/8 byte = 0.125 bytes (Binary Quantization)
    HNSW graph index overhead:
      Each node stores M bi-directional neighbor IDs (typically 16 to 64 uint32 connections per node):
      Overhead approx = num_vectors * hnsw_m * 4 bytes * 2 (accounting for multi-layer hierarchy and pointers)
    """
    precision_bytes = {
        "float32": 4.0,
        "fp16": 2.0,
        "int8": 1.0,
        "binary": 0.125
    }[precision]

    raw_vector_bytes = num_vectors * dimension * precision_bytes
    # HNSW graph connectivity overhead (8 bytes per edge average across layers)
    hnsw_index_bytes = num_vectors * hnsw_m * 8.0
    # Payload metadata stored alongside vectors
    payload_bytes = num_vectors * metadata_bytes_per_doc
    
    total_bytes = raw_vector_bytes + hnsw_index_bytes + payload_bytes
    # Operating system page cache & execution buffer margin (recommended 1.3x)
    total_ram_with_margin_gb = (total_bytes * 1.3) / (1024 ** 3)
    
    return {
        "precision": precision,
        "raw_vectors_mb": round(raw_vector_bytes / (1024 ** 2), 2),
        "hnsw_index_mb": round(hnsw_index_bytes / (1024 ** 2), 2),
        "recommended_ram_gb": round(total_ram_with_margin_gb, 2)
    }

n_docs = 1_000_000 # 1 Million vectors
dim = 1536        # Standard OpenAI / Cohere dimension

fp32_profile = calculate_vector_storage_footprint(n_docs, dim, precision="float32", hnsw_m=16)
int8_profile = calculate_vector_storage_footprint(n_docs, dim, precision="int8", hnsw_m=16)

# float32 raw vectors = 1M * 1536 * 4 bytes = 5,859 MB (~5.86 GB)
assert fp32_profile["raw_vectors_mb"] > 5800
# int8 scalar quantization cuts raw vector memory to 25% (1,464 MB)
assert int8_profile["raw_vectors_mb"] < 1500
assert int8_profile["recommended_ram_gb"] < fp32_profile["recommended_ram_gb"]

print(f"Vector RAM sizing verified: 1M vectors fp32={fp32_profile['recommended_ram_gb']}GB RAM, int8={int8_profile['recommended_ram_gb']}GB RAM")
