"""Polynomial-time reduction from Clique to Independent Set.

A set of vertices is a clique in a graph G if and only if it is an
independent set in the complement graph of G.  Therefore, to decide whether
G has a clique of size at least k, it suffices to decide whether the
complement of G has an independent set of size at least k.

The complement graph is constructed by keeping the same vertex set and
replacing the edge set with all non-edges of the original graph.
"""


def reduce(instance):
    """Return the complement graph as an Independent Set instance.

    The returned instance has the same ``n`` and ``k`` as the input, and its
    edges are exactly the pairs that are *not* edges of the input graph.
    """
    n = instance["n"]
    existing = set()
    for u, v in instance["edges"]:
        if u < v:
            existing.add((u, v))
        else:
            existing.add((v, u))

    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in existing:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": instance["k"]}
