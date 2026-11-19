"""Polynomial-time reduction from Independent Set to Clique.

An independent set in a graph G is exactly a clique in the complement
graph of G.  So the reduction keeps n and k unchanged and replaces the
edge set by its complement on the same vertex set.

Edge cases:
  * k <= 0 : yes for the source, and the target instance also has k <= 0,
             so it is yes as well.
  * k > n  : no for the source, and the target instance has the same n and
             k, so it is no as well.
  * n == 0 : the complement is empty and k > 0 is impossible, matching the
             source (only k <= 0 can be yes).
"""

from __future__ import annotations

from itertools import combinations


def reduce(instance):
    """Map an Independent Set instance to a Clique instance.

    The returned graph is the complement of the input graph; n and k are
    unchanged.
    """
    n = instance["n"]
    k = instance["k"]

    # Canonicalise the existing edges as unordered pairs so that a reversed
    # representation [v, u] is treated the same as [u, v].
    present = set()
    for u, v in instance["edges"]:
        present.add((u, v) if u < v else (v, u))

    complement_edges = [
        [u, v] for u, v in combinations(range(n), 2) if (u, v) not in present
    ]

    return {"n": n, "edges": complement_edges, "k": k}
