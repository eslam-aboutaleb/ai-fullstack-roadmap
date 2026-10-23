"""Demonstrate Hierarchical Navigable Small World (HNSW) multi-layer graph navigation."""
import math

def euclidean_dist(v1, v2):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)))

# Synthetic 2D vectors representing documents in embedding space
nodes = {
    "N0": (1.0, 1.0),
    "N1": (2.0, 2.0),
    "N2": (5.0, 5.0),
    "N3": (8.0, 8.0),
    "N4": (9.0, 9.0)
}

# HNSW Multi-Layer Skip-Graph:
# Layer 2 (Expressway): Sparse long-range connections for fast coarse navigation
# Layer 1 (Regional): Intermediate density
# Layer 0 (Base Layer): Dense short-range Voronoi neighborhood containing all nodes
hnsw_layers = {
    2: {
        "entry_point": "N0",
        "graph": {"N0": ["N3"], "N3": ["N0"]}
    },
    1: {
        "graph": {"N0": ["N1", "N3"], "N1": ["N0", "N2"], "N2": ["N1", "N3"], "N3": ["N2", "N4"], "N4": ["N3"]}
    },
    0: {
        "graph": {
            "N0": ["N1"],
            "N1": ["N0", "N2"],
            "N2": ["N1", "N3"],
            "N3": ["N2", "N4"],
            "N4": ["N3"]
        }
    }
}

def search_hnsw(query_vector):
    """Navigate HNSW graph top-down using greedy nearest-neighbor descent."""
    curr_entry = hnsw_layers[2]["entry_point"]
    visited_layers = []

    # Step 1: Top layers descent (Layers 2 down to 1)
    for level in [2, 1]:
        graph = hnsw_layers[level]["graph"]
        changed = True
        while changed:
            changed = False
            best_dist = euclidean_dist(query_vector, nodes[curr_entry])
            neighbors = graph.get(curr_entry, [])
            for neighbor in neighbors:
                d = euclidean_dist(query_vector, nodes[neighbor])
                if d < best_dist:
                    best_dist = d
                    curr_entry = neighbor
                    changed = True
        visited_layers.append((level, curr_entry))

    # Step 2: Base layer (Layer 0) local greedy walk to exact nearest neighbor
    graph_l0 = hnsw_layers[0]["graph"]
    changed = True
    while changed:
        changed = False
        best_dist = euclidean_dist(query_vector, nodes[curr_entry])
        for neighbor in graph_l0.get(curr_entry, []):
            d = euclidean_dist(query_vector, nodes[neighbor])
            if d < best_dist:
                best_dist = d
                curr_entry = neighbor
                changed = True
    visited_layers.append((0, curr_entry))

    return curr_entry, visited_layers

# Search for query near N4 (8.8, 8.9):
target_query = (8.8, 8.9)
nearest_node, path = search_hnsw(target_query)

assert nearest_node == "N4", f"Expected N4, found {nearest_node}"
print(f"HNSW search verified: target={target_query}, nearest={nearest_node}, navigation_path={path}")
