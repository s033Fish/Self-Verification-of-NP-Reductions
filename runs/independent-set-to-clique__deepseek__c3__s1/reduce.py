"""Polynomial-time reduction from Independent Set to Clique.

An independent set in G is exactly a clique in the complement graph G'.
So we map an instance (n, edges, k) of Independent Set to the instance
(n, complement_edges, k) of Clique, where complement_edges contains every
unordered pair {u, v} with u != v that is NOT an edge of G.

The number of vertices n and the threshold k are unchanged.  This is
correct for all edge cases:
  * k <= 0: both problems are always yes.
  * k > n:  both problems are always no (n is unchanged).
  * k = 1:  an independent set of size >= 1 exists iff n >= 1, and a
            clique of size >= 1 exists iff n >= 1.
"""


def reduce(instance):
    """Reduce an Independent Set instance to a Clique instance.

    Input / output format: {"n": n, "edges": [[u, v], ...], "k": k}
    """
    n = instance["n"]
    k = instance["k"]

    # Normalise the input edges into a set of unordered pairs so that a
    # duplicated or reversed representation cannot affect the result.
    present = set()
    for u, v in instance["edges"]:
        if u > v:
            u, v = v, u
        present.add((u, v))

    # Build the complement graph: all unordered pairs {u, v}, u != v,
    # that are not edges of the original graph.
    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in present:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": k}
