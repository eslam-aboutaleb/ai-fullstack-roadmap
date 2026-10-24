"""Demonstrate zero-downtime Blue/Green embedding migration across production vector collections."""

class VectorStoreRouter:
    def __init__(self):
        # Blue Collection: Active v1 embedding model (dim=1536)
        self.blue_collection = {"doc_1": [0.1] * 1536, "doc_2": [0.2] * 1536}
        # Green Collection: Staged v2 embedding model (dim=3072)
        self.green_collection = {}
        # Active pointer: routing user queries
        self.active_collection = "blue"
        self.is_dual_writing = False

    def start_dual_write_phase(self):
        """Phase 1: Ingestion writes new documents to BOTH Blue (v1) and Green (v2)."""
        self.is_dual_writing = True

    def write_document(self, doc_id, v1_vector, v2_vector):
        self.blue_collection[doc_id] = v1_vector
        if self.is_dual_writing:
            self.green_collection[doc_id] = v2_vector

    def backfill_historical_documents(self, v2_backfill_map):
        """Phase 2: Background worker backfills pre-existing documents into Green collection."""
        for doc_id, v2_vec in v2_backfill_map.items():
            if doc_id not in self.green_collection:
                self.green_collection[doc_id] = v2_vec

    def execute_atomic_cutover(self):
        """Phase 3: Validation passes. Point query router to Green collection atomically."""
        assert len(self.green_collection) == len(self.blue_collection), "Parity check failed before cutover!"
        self.active_collection = "green"

    def query(self, query_vector):
        """Query router dispatches to whichever collection is active."""
        target = self.green_collection if self.active_collection == "green" else self.blue_collection
        # Dimension invariant check:
        for doc_id, vec in target.items():
            if len(query_vector) != len(vec):
                raise ValueError(f"Coordinate mismatch! Query dim {len(query_vector)} != index dim {len(vec)}")
        return f"Searched {self.active_collection} collection with {len(target)} items"

router = VectorStoreRouter()

# Step 1: Pre-migration state (Queries search Blue v1 collection with 1536 dim)
assert router.query([0.5] * 1536) == "Searched blue collection with 2 items"

# Step 2: Start Dual Writing
router.start_dual_write_phase()
router.write_document("doc_3", [0.3] * 1536, [0.3] * 3072)

# Step 3: Backfill doc_1 and doc_2 into Green collection
router.backfill_historical_documents({
    "doc_1": [0.1] * 3072,
    "doc_2": [0.2] * 3072
})

# Step 4: Atomic Cutover to Green collection
router.execute_atomic_cutover()
assert router.active_collection == "green"

# Step 5: Queries now search Green v2 collection with 3072 dim:
result = router.query([0.5] * 3072)
assert result == "Searched green collection with 3 items"

print(f"Blue/Green embedding migration verified: active={router.active_collection}, green_docs={len(router.green_collection)}")

