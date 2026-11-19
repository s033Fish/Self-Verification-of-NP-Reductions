"""Polynomial-time reduction from Clique to Independent Set.

A clique in G is exactly an independent set in the complement graph G'.
So we map an instance (n, edges, k) of Clique to the complement graph on
the same n vertices with the same k.  The reduction runs in O(n^2) time.
"""


def reduce(instance):
    n = instance["n"]
    k = instance["k"]

    # Build a set of the existing undirected edges (normalised to u < v).
    existing = set()
    for u, v in instance["edges"]:
        if u > v:
            u, v = v, u
        existing.add((u, v))

    # Complement graph: keep every non-edge of the original graph.
    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in existing:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": k}
