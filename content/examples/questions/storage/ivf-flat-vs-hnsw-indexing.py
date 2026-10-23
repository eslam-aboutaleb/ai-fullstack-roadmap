"""Compare IVF-Flat (Inverted File) and HNSW (Graph) indexing structures and search mechanics."""
import math

def euclidean_distance(v1, v2):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)))

# 1. IVF-Flat (Inverted File Index) Architecture:
# Partitions the vector space into K clusters (Voronoi cells) around centroids.
# Search inspects only the 'nprobe' closest centroids instead of searching all documents.
class IVFFlatIndex:
    def __init__(self, centroids):
        self.centroids = centroids # dict of centroid_id -> vector
        self.inverted_lists = {cid: [] for cid in centroids} # centroid_id -> list of (doc_id, vector)

    def add(self, doc_id, vector):
        # Assign vector to nearest centroid
        best_cid = min(self.centroids.keys(), key=lambda cid: euclidean_distance(vector, self.centroids[cid]))
        self.inverted_lists[best_cid].append((doc_id, vector))

    def search(self, query_vec, nprobe=1, top_k=2):
        # Step 1: Find nprobe closest centroids
        closest_centroids = sorted(
            self.centroids.keys(), key=lambda cid: euclidean_distance(query_vec, self.centroids[cid])
        )[:nprobe]
        
        # Step 2: Exhaustively search vectors only within these nprobe inverted lists
        candidates = []
        for cid in closest_centroids:
            for doc_id, vec in self.inverted_lists[cid]:
                candidates.append((doc_id, euclidean_distance(query_vec, vec)))
                
        candidates.sort(key=lambda x: x[1])
        return candidates[:top_k]

# Test Case:
# 2 Centroids
centroids = {
    "cluster_left": [1.0, 1.0],
    "cluster_right": [9.0, 9.0]
}
ivf = IVFFlatIndex(centroids)
ivf.add("doc_L1", [1.1, 1.2])
ivf.add("doc_L2", [0.9, 0.8])
ivf.add("doc_R1", [8.9, 9.1])
ivf.add("doc_R2", [9.2, 8.8])

# Query near left cluster:
query = [1.0, 0.9]
# With nprobe=1, IVF-Flat prunes cluster_right completely and searches only cluster_left!
results = ivf.search(query, nprobe=1, top_k=2)

assert len(results) == 2
assert results[0][0] in ["doc_L1", "doc_L2"]
assert not any("doc_R" in r[0] for r in results)

print(f"IVF-Flat index verified: query={query}, top_matches={[r[0] for r in results]} (pruned cluster_right)")
