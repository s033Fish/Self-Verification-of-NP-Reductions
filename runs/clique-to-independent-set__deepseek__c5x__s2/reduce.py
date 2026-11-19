"""Polynomial-time reduction from Clique to Independent Set.

Construction: complement graph.
    A set S of vertices is a clique in G  <=>  S is an independent set in
    the complement graph G'.  So we keep n and k unchanged and replace the
    edge set by its complement (all pairs {u, v} with u < v that are NOT
    edges of G).

This preserves the "at least k" threshold exactly, and therefore also all
edge cases: k <= 0 stays yes, k > n stays no (n is unchanged), k = 1 works
because a single vertex is trivially independent.

The construction runs in O(n^2) time.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Clique instance to an Independent Set instance.

    Input / output format: {"n": n, "edges": [[u, v], ...], "k": k}
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    original = {frozenset(edge) for edge in edges}

    complement_edges = [
        [u, v]
        for u in range(n)
        for v in range(u + 1, n)
        if frozenset((u, v)) not in original
    ]

    return {"n": n, "edges": complement_edges, "k": k}
