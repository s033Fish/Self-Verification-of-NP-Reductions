"""Polynomial-time reduction from Vertex Cover to Clique.

Given a Vertex Cover instance G = (V, E) and integer k, construct the
complement graph H = (V, complement(E)) and set k' = n - k.

A set C is a vertex cover of G iff V \ C is a clique in H.  Therefore G has
a vertex cover of size at most k iff H has a clique of size at least n - k.
The construction runs in O(n^2) time.
"""


def reduce(instance):
    n = instance["n"]
    k = instance["k"]

    # Normalize the source edges so lookups are orientation-independent.
    source_edges = set()
    for edge in instance.get("edges", []):
        u, v = edge
        if u > v:
            u, v = v, u
        source_edges.add((u, v))

    # Build the complement graph on the same vertex set.
    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in source_edges:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": n - k}
