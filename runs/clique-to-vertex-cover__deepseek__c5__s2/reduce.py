"""Polynomial-time reduction from Clique to Vertex Cover.

Key fact: a set S is a clique in G exactly when S is an independent set in
the complement graph G'.  A set C is a vertex cover of G' exactly when its
complement V \\ C is an independent set of G'.  Therefore G has a clique of
size >= k iff G' has an independent set of size >= k iff G' has a vertex
cover of size <= n - k.

Reduction: map (G, k) to (complement(G), n - k).
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Clique instance to a Vertex Cover instance.

    Input:  {"n": n, "edges": [[u, v], ...], "k": k}   (Clique)
    Output: {"n": n, "edges": [[u, v], ...], "k": n-k} (Vertex Cover)
            where the output edges are exactly the non-edges of the input
            graph (the complement graph).
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    present: set[frozenset[int]] = set()
    for u, v in edges:
        present.add(frozenset((u, v)))

    complement: list[list[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in present:
                complement.append([u, v])

    return {"n": n, "edges": complement, "k": n - k}
