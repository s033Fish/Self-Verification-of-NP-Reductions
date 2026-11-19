"""Polynomial-time reduction from Clique to Independent Set.

A set S of vertices is a clique in G exactly when S is an independent set in
the complement graph of G.  Therefore the reduction maps a Clique instance
(n, edges, k) to the Independent Set instance (n, complement_edges, k), where
the complement graph has an edge between every pair of distinct vertices that
is *not* an edge of G.  The required size k is unchanged, so the answer is
preserved, including the edge cases k <= 0 and k > n.

Building the complement takes O(n^2) time (and O(n^2) output space), which is
polynomial in the instance size.  No brute-force solver is called.
"""

from __future__ import annotations

from itertools import combinations
from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Clique instance to an Independent Set instance.

    The returned instance is the complement graph with the same ``k``.
    """
    n = instance["n"]
    k = instance["k"]

    # Record the existing undirected edges in a canonical way so that
    # [u, v] and [v, u] are recognised as the same edge.
    existing = {frozenset((u, v)) for u, v in instance["edges"]}

    # Every pair of distinct vertices absent from G becomes an edge of the
    # complement graph.  combinations yields u < v, so each edge is emitted
    # once and no self-loops are produced.
    complement_edges = [
        [u, v]
        for u, v in combinations(range(n), 2)
        if frozenset((u, v)) not in existing
    ]

    return {"n": n, "edges": complement_edges, "k": k}
