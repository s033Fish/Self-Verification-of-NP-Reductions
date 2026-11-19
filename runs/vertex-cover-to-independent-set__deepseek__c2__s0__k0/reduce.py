"""Polynomial-time reduction from Vertex Cover to Independent Set.

A set S is a vertex cover of G = (V, E) if and only if its complement
V \ S is an independent set of G.  Consequently G has a vertex cover of
size AT MOST k if and only if G has an independent set of size AT LEAST
n - k.  The reduction therefore keeps the graph unchanged and maps the
budget k to n - k.

This is correct for every integer k, including the edge cases:
  * k < 0      -> n - k > n, and Independent Set is always no for k > n.
  * k >= n     -> n - k <= 0, and Independent Set is always yes for k <= 0.
  * no edges   -> both sides are yes (for k >= 0 / n - k <= n).
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Vertex Cover instance to an Independent Set instance.

    Input : {"n": n, "edges": [[u, v], ...], "k": k}   (Vertex Cover)
    Output: {"n": n, "edges": [[u, v], ...], "k": n-k} (Independent Set)
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Copy the edge list so the returned instance is independent of the input.
    new_edges = [[u, v] for u, v in edges]

    return {"n": n, "edges": new_edges, "k": n - k}
