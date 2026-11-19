"""Polynomial-time reduction from Clique to Vertex Cover.

Construction
------------
Given a Clique instance (G, k) on n vertices, build the complement graph
G' = (V, E') where E' contains exactly the non-edges of G (including no
self-loops).  Return the VertexCover instance (G', n - k).

Correctness
-----------
A set C is a clique in G iff V \\ C is a vertex cover of G':
  * If C is a clique, then every non-edge of G has at least one endpoint
    outside C (otherwise both endpoints would be in C and adjacent in G),
    so V \\ C covers every edge of G'.
  * Conversely, if V \\ C is a vertex cover of G', then no non-edge of G has
    both endpoints in C, so every pair in C is an edge of G: C is a clique.

Hence G has a clique of size >= k iff G' has a vertex cover of size <= n-k.
This also matches the edge cases: k <= 0 gives n-k >= n (always yes for
Vertex Cover), and k > n gives n-k < 0 (always no).

The construction runs in O(n^2) time.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Clique instance to a Vertex Cover instance."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Edge set of the input graph, normalised as frozensets.
    present = {frozenset((u, v)) for u, v in edges}

    complement: list[list[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in present:
                complement.append([u, v])

    return {"n": n, "edges": complement, "k": n - k}
