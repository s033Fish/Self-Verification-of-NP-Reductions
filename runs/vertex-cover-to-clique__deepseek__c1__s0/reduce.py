"""Polynomial-time reduction from Vertex Cover to Clique.

Given a Vertex Cover instance (G, k), construct the complement graph H on the
same vertex set and set k' = n - k.  A set S is a vertex cover of G iff its
complement V \ S is an independent set in G, which is exactly a clique in H.
Therefore G has a vertex cover of size at most k iff H has a clique of size at
least n - k.
"""


def reduce(instance):
    n = instance["n"]
    k = instance["k"]

    # Normalize the input edges so each undirected edge is stored once as
    # (min(u, v), max(u, v)).
    existing = set()
    for u, v in instance["edges"]:
        if u > v:
            u, v = v, u
        existing.add((u, v))

    # Build the complement graph on vertices 0..n-1.
    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in existing:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": n - k}
