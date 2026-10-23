"""Demonstrate Write-Ahead Logging (WAL) and crash recovery for in-memory vector index persistence."""
import json
import os
import tempfile

class PersistentVectorIndex:
    def __init__(self, wal_path):
        self.wal_path = wal_path
        self.in_memory_index = {} # doc_id -> vector
        self.recover_from_wal()

    def insert(self, doc_id, vector):
        """
        Write-Ahead Logging:
        1. Write insertion record to append-only disk log and flush (fsync).
        2. Only after disk persistence is confirmed, mutate volatile in-memory index.
        """
        entry = {"op": "INSERT", "id": doc_id, "vec": vector}
        with open(self.wal_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
            f.flush()
            os.fsync(f.fileno())

        self.in_memory_index[doc_id] = vector

    def recover_from_wal(self):
        """Replay uncompacted WAL entries on startup to rebuild in-memory index after a crash."""
        if not os.path.exists(self.wal_path):
            return
        with open(self.wal_path, "r") as f:
            for line in f:
                if not line.strip(): continue
                entry = json.loads(line)
                if entry["op"] == "INSERT":
                    self.in_memory_index[entry["id"]] = entry["vec"]

wal_file = os.path.join(tempfile.gettempdir(), "test_vector_wal.log")
if os.path.exists(wal_file):
    os.remove(wal_file)

try:
    # Process 1: Inserts records and experiences simulated crash / kill -9
    idx1 = PersistentVectorIndex(wal_file)
    idx1.insert("doc_1", [0.12, 0.45])
    idx1.insert("doc_2", [0.88, 0.92])
    assert len(idx1.in_memory_index) == 2

    # SIMULATE SUDDEN CRASH: Discard in-memory instance without graceful shutdown
    del idx1

    # Process 2: Server restarts and initializes new PersistentVectorIndex
    idx2 = PersistentVectorIndex(wal_file)
    
    # Verify that WAL replay restored 100% of persisted vectors:
    assert len(idx2.in_memory_index) == 2
    assert idx2.in_memory_index["doc_1"] == [0.12, 0.45]
    assert idx2.in_memory_index["doc_2"] == [0.88, 0.92]

    print(f"Vector WAL crash recovery verified: restored_records={len(idx2.in_memory_index)} from WAL log")
finally:
    if os.path.exists(wal_file):
        os.remove(wal_file)
