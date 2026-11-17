"""Polynomial-time reduction from Clique to Independent Set.

A clique in a graph G is exactly an independent set in the complement graph
of G.  Therefore, given a Clique instance (G, k) we output the Independent Set
instance (complement(G), k).  This keeps n and k unchanged and only rebuilds
the edge set, which takes O(n^2) time.
"""


def _complement_edges(n, edges):
    """Return the edges of the complement graph on vertices 0..n-1.

    The output is a list of pairs [u, v] with u < v, no duplicates, matching
    the instance format documented for IndependentSet.
    """
    present = set()
    for edge in edges:
        u, v = edge
        if u > v:
            u, v = v, u
        present.add((u, v))

    complement = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in present:
                complement.append([u, v])
    return complement


def reduce(instance):
    """Reduce a Clique instance to an Independent Set instance."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    return {"n": n, "edges": _complement_edges(n, edges), "k": k}
