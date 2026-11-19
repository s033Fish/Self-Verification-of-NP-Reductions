"""Polynomial-time reduction from Independent Set to Clique.

Reduction: an independent set in G is exactly a clique in the complement
graph of G.  So keep n and k, and replace the edge set by its complement
(all pairs {u, v} with u < v that are NOT edges of G).

Correctness:
  * k <= 0: source is yes (empty set) and target is yes (empty set).
  * k > n:  source is no and target is no (a clique has at most n vertices).
  * 0 < k <= n: a set S of k vertices is independent in G iff every pair in
    S is a non-edge of G iff every pair in S is an edge of the complement,
    i.e. S is a clique in the complement.  Hence the answers agree.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    original = {frozenset((u, v)) for u, v in edges}
    complement = [
        [u, v]
        for u in range(n)
        for v in range(u + 1, n)
        if frozenset((u, v)) not in original
    ]

    return {"n": n, "edges": complement, "k": k}
