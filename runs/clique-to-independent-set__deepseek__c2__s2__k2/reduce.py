"""Polynomial-time reduction from Clique to Independent Set.

Given a Clique instance G = (V, E), k, construct the complement graph
G' = (V, E') where E' contains exactly the unordered pairs {u, v}
(u != v) that are NOT edges of G.  Keep the same n and the same k.

A set S of vertices is a clique in G iff it is an independent set in G'.
Therefore G has a clique of size at least k iff G' has an independent
set of size at least k.  The construction runs in O(n^2) time.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Normalize the given edges into a set of unordered pairs.
    given = set()
    for u, v in edges:
        if u > v:
            u, v = v, u
        given.add((u, v))

    # Complement edges: every pair u < v not present in the original graph.
    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in given:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": k}
