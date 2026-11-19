"""Polynomial-time reduction from Independent Set to Clique.

An independent set in a graph G is exactly a clique in the complement
graph of G.  Therefore, given an Independent Set instance
{"n": n, "edges": E, "k": k}, we return the Clique instance
{"n": n, "edges": E', "k": k}, where E' consists of every unordered pair
{u, v} of distinct vertices that is not present in E.

The number of vertices n and the threshold k are unchanged, so the
"at least k" semantics are preserved exactly, including the edge cases
k <= 0 and k > n.
"""

from itertools import combinations


def reduce(instance):
    """Reduce an Independent Set instance to a Clique instance.

    The returned instance has the same n and k, and its edge set is the
    complement of the input edge set.  Runs in O(n^2) time.
    """
    n = instance["n"]
    k = instance["k"]

    # Normalize the input edges as unordered pairs so that the
    # complement is computed correctly regardless of endpoint order.
    existing = set()
    for u, v in instance["edges"]:
        existing.add((u, v) if u <= v else (v, u))

    complement_edges = [
        [u, v]
        for u, v in combinations(range(n), 2)
        if (u, v) not in existing
    ]

    return {"n": n, "edges": complement_edges, "k": k}
