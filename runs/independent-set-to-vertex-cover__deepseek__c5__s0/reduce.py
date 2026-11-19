"""Polynomial-time reduction from Independent Set to Vertex Cover.

Key fact: S is an independent set in G = (V, E) if and only if V \\ S is a
vertex cover of G.  Therefore G has an independent set of size >= k iff G
has a vertex cover of size <= n - k.  The reduction keeps the same graph
and maps the parameter k to n - k.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict) -> dict:
    """Reduce an Independent Set instance to a Vertex Cover instance.

    Input : {"n": n, "edges": [[u, v], ...], "k": k}   (Independent Set)
    Output: {"n": n, "edges": [[u, v], ...], "k": n - k} (Vertex Cover)

    A set S is independent iff its complement V \\ S is a vertex cover, so
    the graph has an independent set of size >= k exactly when it has a
    vertex cover of size <= n - k.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    return {"n": n, "edges": [list(e) for e in edges], "k": n - k}
