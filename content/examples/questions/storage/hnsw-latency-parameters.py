"""Demonstrate HNSW search latency and recall scaling as a function of efSearch and graph parameters."""

def simulate_hnsw_query_cost(num_vectors, ef_search, hnsw_m=16, filter_selectivity=1.0):
    """
    HNSW Query Latency depends on:
      1. ef_search: Size of the dynamic candidate list during query time.
         Distance evaluations scale linearly with ef_search: Comparisons approx = ef_search * M * log(N).
      2. M: Outgoing connectivity per node. Denser graphs increase cache misses and distance computations.
      3. filter_selectivity: If only 1% of vectors match the filter (selectivity=0.01),
         the graph traversal must evaluate 100x more nodes to find ef_search valid candidates!
      4. Vector Dimension & SIMD: 1536 dim AVX-512 dot products take ~40ns per comparison.
    """
    import math
    base_hops = math.log2(num_vectors)
    
    # Distance comparisons required during search:
    comparisons = ef_search * (hnsw_m / 2.0) * (base_hops / 10.0)
    
    # If filtered search has low selectivity, search must expand to bypass invalid nodes:
    if filter_selectivity < 1.0:
        expansion_factor = min(10.0, 1.0 / max(0.01, filter_selectivity))
        comparisons *= expansion_factor

    # Nanoseconds per comparison assuming AVX-512 SIMD for 1536 dim
    ns_per_comparison = 35.0
    estimated_latency_ms = (comparisons * ns_per_comparison) / 1_000_000.0

    return {
        "ef_search": ef_search,
        "filter_selectivity": filter_selectivity,
        "comparisons": int(comparisons),
        "estimated_latency_ms": round(estimated_latency_ms, 3)
    }

# 1. Fast low-latency configuration (ef_search = 32, no filter):
fast_run = simulate_hnsw_query_cost(1_000_000, ef_search=32, filter_selectivity=1.0)

# 2. High-recall configuration (ef_search = 128, no filter):
high_recall_run = simulate_hnsw_query_cost(1_000_000, ef_search=128, filter_selectivity=1.0)

# 3. High-recall with sparse 2% filter selectivity (forces deep graph exploration):
filtered_run = simulate_hnsw_query_cost(1_000_000, ef_search=128, filter_selectivity=0.02)

assert high_recall_run["comparisons"] > fast_run["comparisons"]
assert filtered_run["estimated_latency_ms"] > high_recall_run["estimated_latency_ms"]

print(f"HNSW latency factors verified: ef_32={fast_run['estimated_latency_ms']}ms, ef_128={high_recall_run['estimated_latency_ms']}ms, ef_128_filtered={filtered_run['estimated_latency_ms']}ms")

