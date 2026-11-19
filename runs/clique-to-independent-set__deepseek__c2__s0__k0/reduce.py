"""Polynomial-time reduction from Clique to Independent Set.

A clique in a graph G is exactly an independent set in the complement
graph of G.  So the reduction keeps ``n`` and ``k`` and replaces the edge
set by its complement: the edge set of the complete graph on ``n``
vertices minus the edges of G.

This is computable in O(n^2) time and preserves the answer for every
instance, including the edge cases (``k <= 0`` is always yes, ``k > n``
is always no, and both problems share the same ``n``).
"""

from itertools import combinations


def reduce(instance):
    """Map a Clique instance to an Independent Set instance.

    The returned instance has the same ``n`` and ``k`` as the input, and
    its edges are precisely the non-edges of the input graph.
    """
    n = instance["n"]
    k = instance["k"]

    # Existing edges as an unordered set of vertex pairs.
    present = set()
    for u, v in instance["edges"]:
        present.add((u, v) if u < v else (v, u))

    # Complement edges: every pair of distinct vertices not already an edge.
    edges = [[u, v] for u, v in combinations(range(n), 2) if (u, v) not in present]

    return {"n": n, "edges": edges, "k": k}
