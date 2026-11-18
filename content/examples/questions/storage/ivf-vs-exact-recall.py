"""IVF searches only the closest lists; probes trade recall for fewer distance computations."""
import math

POINTS = {
    "a1": (0.0, 0.0), "a2": (1.0, 1.0), "a3": (0.5, 2.0),
    "b1": (10.0, 0.0), "b2": (9.0, 1.0), "b3": (6.0, 0.4),
    "c1": (5.0, 10.0), "c2": (6.0, 9.0),
}
CENTROIDS = {"A": (0.5, 1.0), "B": (8.5, 0.5), "C": (5.5, 9.5)}


def assign():
    lists = {name: [] for name in CENTROIDS}
    for pid, p in POINTS.items():
        lists[min(CENTROIDS, key=lambda c: math.dist(p, CENTROIDS[c]))].append(pid)
    return lists


def search(query, lists, probes):
    chosen = sorted(CENTROIDS, key=lambda c: math.dist(query, CENTROIDS[c]))[:probes]
    candidates = [pid for c in chosen for pid in lists[c]]
    best = min(candidates, key=lambda pid: math.dist(query, POINTS[pid]))
    return best, len(candidates)


lists = assign()
query = (4.2, 0.3)
exact = min(POINTS, key=lambda pid: math.dist(query, POINTS[pid]))
one = search(query, lists, 1)
two = search(query, lists, 2)
assert exact == "b3" and one[0] != exact and two[0] == exact
print("exact", exact, "probes1", one, "probes2", two, "total", len(POINTS))
