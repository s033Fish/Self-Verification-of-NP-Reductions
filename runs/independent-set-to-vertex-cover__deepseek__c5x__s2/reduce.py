r"""Polynomial-time reduction from Independent Set to Vertex Cover.

Key fact: for a graph G = (V, E), a set S is an independent set if and only
if its complement V \ S is a vertex cover.  Therefore G has an independent
set of size at least k exactly when G has a vertex cover of size at most
n - k.  The reduction keeps the graph unchanged and maps k -> n - k.

This also handles the documented edge cases:
  * k <= 0: source yes; target k' = n - k >= n, and k' >= n is always yes.
  * k > n:  source no;  target k' = n - k < 0, and k' < 0 is always no.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce an Independent Set instance to a Vertex Cover instance.

    Instance format (both problems):
        {"n": n, "edges": [[u, v], ...], "k": k}
    """
    n = instance["n"]
    edges = [[u, v] for u, v in instance["edges"]]
    k = instance["k"]
    return {"n": n, "edges": edges, "k": n - k}
