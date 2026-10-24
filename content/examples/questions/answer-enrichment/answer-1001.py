from collections import deque
graph = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": ["A"]}
queue = deque([("A", 0)])
seen = {"A"}
distance = {}
while queue:
    node, depth = queue.popleft()
    distance[node] = depth
    for neighbor in graph[node]:
        if neighbor not in seen:
            seen.add(neighbor)
            queue.append((neighbor, depth + 1))
assert distance == {"A": 0, "B": 1, "C": 1, "D": 2}
print("A:0 B:1 C:1 D:2; cycle terminates")
