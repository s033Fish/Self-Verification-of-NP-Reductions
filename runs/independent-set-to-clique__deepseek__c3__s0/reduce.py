"""Polynomial-time reduction from Independent Set to Clique.

An independent set in G is exactly a clique in the complement graph of G,
so the reduction keeps n and k unchanged and replaces the edge list by the
complement edge list.  Building the complement takes O(n^2) time.
"""

from itertools import combinations


def reduce(instance):
    """Map an IndependentSet instance to a Clique instance.

    Instance format (both problems):
        {"n": n, "edges": [[u, v], ...], "k": k}

    The complement graph has an edge between u and v exactly when the
    original graph does not.  A set of vertices is independent in the
    original graph iff it is a clique in the complement, so the yes/no
    answer is preserved, including the k <= 0 and k > n edge cases.
    """
    n = instance["n"]
    k = instance["k"]
    original = {frozenset((u, v)) for u, v in instance["edges"]}
    complement_edges = [
        [u, v]
        for u, v in combinations(range(n), 2)
        if frozenset((u, v)) not in original
    ]
    return {"n": n, "edges": complement_edges, "k": k}
