"""Implement single-stage Filtered HNSW graph traversal using metadata predicate masks."""
import math

def euclidean_dist(v1, v2):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)))

class FilteredHNSWGraph:
    def __init__(self):
        # Nodes: id -> {vector, tenant, status}
        self.nodes = {
            "n1": {"vec": [1.0, 1.0], "tenant": "tenant_acme", "status": "active"},
            "n2": {"vec": [1.2, 1.1], "tenant": "tenant_other", "status": "active"}, # High similarity but wrong tenant!
            "n3": {"vec": [1.5, 1.4], "tenant": "tenant_acme", "status": "active"},
            "n4": {"vec": [8.0, 8.0], "tenant": "tenant_acme", "status": "archived"}
        }
        # Graph adjacency edges:
        self.edges = {
            "n1": ["n2", "n3"],
            "n2": ["n1", "n3"],
            "n3": ["n1", "n2", "n4"],
            "n4": ["n3"]
        }

    def search_filtered(self, query_vec, target_tenant, target_status="active", top_k=2):
        """
        Single-stage Filtered HNSW:
        Evaluates metadata predicates inside the greedy graph traversal loop.
        Neighbors that fail the tenant predicate are never emitted into the final result set,
        preventing candidate starvation.
        """
        entry_node = "n1"
        visited = set([entry_node])
        candidates = [(euclidean_dist(query_vec, self.nodes[entry_node]["vec"]), entry_node)]
        
        # Priority greedy walk
        eligible_results = []
        
        while candidates:
            candidates.sort(key=lambda x: x[0])
            curr_dist, curr_id = candidates.pop(0)
            node_data = self.nodes[curr_id]
            
            # Predicate check:
            if node_data["tenant"] == target_tenant and node_data["status"] == target_status:
                eligible_results.append((curr_id, curr_dist))
                if len(eligible_results) == top_k:
                    break

            for neighbor in self.edges.get(curr_id, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    d = euclidean_dist(query_vec, self.nodes[neighbor]["vec"])
                    candidates.append((d, neighbor))

        return eligible_results

graph = FilteredHNSWGraph()
query = [1.1, 1.0]

# Search with tenant filter = 'tenant_acme' and status = 'active':
# Notice: 'n2' has vector [1.2, 1.1] which is closest to query, BUT it belongs to 'tenant_other'.
# Filtered HNSW traversal skips 'n2' for results and selects 'n1' and 'n3' belonging to 'tenant_acme':
results = graph.search_filtered(query, target_tenant="tenant_acme", top_k=2)

assert len(results) == 2
result_ids = [r[0] for r in results]
assert "n1" in result_ids and "n3" in result_ids
assert "n2" not in result_ids, "Cross-tenant candidate filtered out"

print(f"Filtered HNSW verified: query={query}, target_tenant=tenant_acme, selected_nodes={result_ids}")
