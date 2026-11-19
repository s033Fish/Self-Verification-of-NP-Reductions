"""Polynomial-time reduction from Clique to Vertex Cover.

A set S is a clique of size at least k in G exactly when its complement
V \\ S is a vertex cover of size at most n - k in the complement graph.
Thus we map (G, k) to (complement(G), n - k).
"""


def reduce(instance):
    """Return a Vertex Cover instance equivalent to the Clique instance.

    The returned instance has the same vertex set, the complement edge set,
    and k' = n - k.
    """
    n = instance["n"]
    k = instance["k"]

    # Normalize the input edges and record them in a set.  The problem
    # guarantees undirected edges are not duplicated, but normalizing makes
    # the construction robust to either orientation.
    existing = set()
    for u, v in instance["edges"]:
        if u > v:
            u, v = v, u
        existing.add((u, v))

    # Build the complement graph: include every non-loop pair not in G.
    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in existing:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": n - k}
