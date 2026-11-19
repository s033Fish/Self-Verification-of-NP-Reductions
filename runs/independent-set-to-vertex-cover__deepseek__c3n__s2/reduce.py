r"""Polynomial-time reduction from Independent Set to Vertex Cover.

Key fact: a set S is independent in G = (V, E) iff its complement V \ S is a
vertex cover of G.  Hence G has an independent set of size >= k iff G has a
vertex cover of size <= n - k.

So the reduction keeps the graph unchanged and maps k -> n - k.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce an Independent Set instance to a Vertex Cover instance.

    Input:  {"n": n, "edges": [[u, v], ...], "k": k}   (Independent Set)
    Output: {"n": n, "edges": [[u, v], ...], "k": n - k} (Vertex Cover)
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Copy edges so the returned instance shares no mutable structure.
    return {"n": n, "edges": [list(edge) for edge in edges], "k": n - k}
