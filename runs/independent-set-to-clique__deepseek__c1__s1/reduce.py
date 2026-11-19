"""Polynomial-time reduction from Independent Set to Clique.

An independent set in a graph G is exactly a clique in the complement
graph of G.  Therefore the instance (G, k) of Independent Set is a yes
instance iff (complement(G), k) is a yes instance of Clique.

The complement is built in O(n^2) time, so the reduction is polynomial.
"""


def reduce(instance):
    """Reduce an Independent Set instance to a Clique instance.

    Input/output format:
        {"n": n, "edges": [[u, v], ...], "k": k}

    The returned instance is the complement graph on the same n vertices
    with the same k.
    """
    n = instance["n"]
    k = instance["k"]

    # Record the existing edges as unordered pairs so membership tests are
    # O(1).  frozenset handles both [u, v] and [v, u] representations.
    present = {frozenset((u, v)) for u, v in instance["edges"]}

    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in present:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": k}
