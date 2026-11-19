"""Reduction from Clique to Vertex Cover.

Given an instance of Clique:
    {"n": n, "edges": [[u, v], ...], "k": k}
we produce an instance of VertexCover on the complement graph with
parameter k' = n - k.

The reduction runs in polynomial time (O(n^2)).
"""

def reduce(instance):
    n = instance["n"]
    k = instance["k"]
    # Build a set of existing edges for quick lookup (undirected).
    edge_set = set()
    for u, v in instance["edges"]:
        if u > v:
            u, v = v, u
        edge_set.add((u, v))
    # Complement edges: all unordered pairs not present in edge_set.
    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in edge_set:
                complement_edges.append([u, v])
    # New parameter for Vertex Cover.
    k_prime = n - k
    return {"n": n, "edges": complement_edges, "k": k_prime}

# The module may be imported by the evaluation harness which expects a
# function named `reduce`.
