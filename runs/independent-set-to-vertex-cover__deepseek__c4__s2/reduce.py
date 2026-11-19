"""Polynomial-time reduction from Independent Set to Vertex Cover.

Key fact: a vertex set S is an independent set in G = (V, E) if and only if
its complement V \\ S is a vertex cover of G.  Therefore G has an independent
set of size >= k iff G has a vertex cover of size <= n - k.

Reduction: keep the graph unchanged and map k -> n - k.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce an Independent Set instance to a Vertex Cover instance.

    Input:  {"n": n, "edges": [...], "k": k}   (Independent Set)
    Output: {"n": n, "edges": [...], "k": n-k} (Vertex Cover)
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    return {"n": n, "edges": [list(e) for e in edges], "k": n - k}
