"""Polynomial-time reduction from Vertex Cover to Independent Set.

Key fact: a set S of vertices is a vertex cover of G = (V, E) if and only if
its complement V \\ S is an independent set of G.  Therefore G has a vertex
cover of size AT MOST k exactly when G has an independent set of size AT LEAST
n - k.  The reduction keeps the graph unchanged and maps k -> n - k.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Vertex Cover instance to an Independent Set instance.

    Input : {"n": n, "edges": [[u, v], ...], "k": k}   (Vertex Cover)
    Output: {"n": n, "edges": [[u, v], ...], "k": n-k} (Independent Set)

    The graph is copied (edges are copied too, so the input is not aliased)
    and the threshold is complemented.  Runs in O(|E|) time.
    """
    n = instance["n"]
    edges = [[u, v] for u, v in instance["edges"]]
    k = instance["k"]
    return {"n": n, "edges": edges, "k": n - k}
