"""Polynomial-time reduction from Independent Set to Clique.

A vertex subset S is independent in G exactly when S is a clique in the
complement graph of G.  Therefore we map an Independent Set instance
(n, edges, k) to the Clique instance (n, complement_edges, k), where the
complement contains exactly the pairs {u, v} that are NOT edges of G.
"""

from itertools import combinations


def reduce(instance):
    """Return the Clique instance corresponding to an Independent Set instance.

    The graph is replaced by its complement; n and k are unchanged.
    """
    n = instance["n"]
    k = instance["k"]

    # Normalise the given edges to frozensets so that [u, v] and [v, u]
    # are treated as the same edge, then build the complement.
    given = {frozenset((u, v)) for u, v in instance["edges"]}

    complement_edges = [
        [u, v]
        for u, v in combinations(range(n), 2)
        if frozenset((u, v)) not in given
    ]

    return {"n": n, "edges": complement_edges, "k": k}
