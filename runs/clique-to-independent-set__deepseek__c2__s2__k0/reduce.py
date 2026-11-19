"""Polynomial-time reduction from Clique to Independent Set.

A clique in a graph G is exactly an independent set in the complement graph
of G.  Therefore, given a Clique instance (n, edges, k), we return the
Independent Set instance on the same number of vertices whose edge set is
the complement of the original edge set, keeping k unchanged.

The complement is computed in O(n^2) time (which is polynomial in the
instance size), and the transformation preserves the answer:
    G has a clique of size >= k
        <=> complement(G) has an independent set of size >= k.

Edge cases are preserved automatically since n and k are unchanged:
    * k <= 0 is yes for both problems.
    * k > n is no for both problems.
"""


def reduce(instance):
    n = instance["n"]
    k = instance["k"]

    # Normalise the original edges into a set of unordered pairs.
    original = set()
    for u, v in instance["edges"]:
        original.add((u, v) if u < v else (v, u))

    # The complement contains every non-loop pair not present in the original.
    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in original:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": k}
