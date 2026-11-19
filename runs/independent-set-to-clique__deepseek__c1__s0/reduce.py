"""Polynomial-time reduction from Independent Set to Clique.

Given an Independent Set instance G = (V, E), construct its complement graph
G' = (V, all pairs {u, v} not in E).  A set S is independent in G iff S is a
clique in G'.  Therefore the same k works for both instances.
"""


def reduce(instance):
    """Return the complement graph as a Clique instance.

    The input and output both use the format:
        {"n": n, "edges": [[u, v], ...], "k": k}
    """
    n = instance["n"]
    k = instance["k"]

    # Normalize source edges so reversed duplicates and self-loops do not
    # affect the complement construction.
    source_edges = set()
    for edge in instance["edges"]:
        u, v = edge[0], edge[1]
        if u == v:
            continue
        if u > v:
            u, v = v, u
        source_edges.add((u, v))

    # The complement contains exactly the non-edges of the source graph.
    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in source_edges:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": k}
