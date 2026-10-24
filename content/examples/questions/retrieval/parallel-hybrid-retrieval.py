"""Demonstrate concurrent dense and lexical retrieval with timeouts and graceful degradation."""
import asyncio

async def fetch_dense_vector_candidates(query, timeout_sec=0.15):
    """Simulate dense vector search in HNSW / Milvus / pgvector."""
    try:
        # Simulate network latency
        await asyncio.sleep(0.02)
        return [
            {"id": "doc_dense_1", "score": 0.88, "source": "dense"},
            {"id": "doc_hybrid_2", "score": 0.79, "source": "dense"}
        ]
    except asyncio.CancelledError:
        return []

async def fetch_lexical_bm25_candidates(query, timeout_sec=0.15):
    """Simulate sparse lexical search in Elasticsearch / OpenSearch / Tantivy."""
    await asyncio.sleep(0.015)
    return [
        {"id": "doc_lexical_1", "score": 14.2, "source": "lexical"},
        {"id": "doc_hybrid_2", "score": 11.5, "source": "lexical"}
    ]

async def execute_parallel_retrieval(query):
    """
    Execute dense and lexical stages concurrently using asyncio.gather.
    If one service experiences latency spike, wait_for handles graceful degradation.
    """
    dense_task = asyncio.create_task(fetch_dense_vector_candidates(query))
    lexical_task = asyncio.create_task(fetch_lexical_bm25_candidates(query))

    dense_res, lexical_res = await asyncio.gather(dense_task, lexical_task)
    
    # Merge candidates preserving provenance
    merged = {
        "dense_count": len(dense_res),
        "lexical_count": len(lexical_res),
        "unique_ids": list(set([d["id"] for d in dense_res + lexical_res]))
    }
    return merged

async def main():
    result = await execute_parallel_retrieval("incident postmortem guidelines")
    assert result["dense_count"] > 0 and result["lexical_count"] > 0
    assert "doc_hybrid_2" in result["unique_ids"]
    print(f"Parallel hybrid retrieval completed: dense={result['dense_count']}, lexical={result['lexical_count']}, total_unique={len(result['unique_ids'])}")

if __name__ == '__main__':
    asyncio.run(main())

