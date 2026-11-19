"""Polynomial-time reduction from Independent Set to Clique.

For an Independent Set instance with graph G = (V, E), the reduction
returns the Clique instance on the complement graph H = (V, E_complement),
keeping n and k unchanged.

A vertex set S is independent in G exactly when S is a clique in H:
for every pair u, v in S, G has no edge (u, v) iff H has edge (u, v).
Therefore G has an independent set of size at least k iff H has a clique
of size at least k.
"""


def reduce(instance):
    """Reduce an Independent Set instance to a Clique instance."""
    n = instance["n"]
    k = instance["k"]

    # Store the original edges as unordered pairs.
    original_edges = set()
    for u, v in instance["edges"]:
        if u == v:
            continue
        if u > v:
            u, v = v, u
        original_edges.add((u, v))

    # The complement graph has an edge for every non-edge of the source.
    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in original_edges:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": k}
