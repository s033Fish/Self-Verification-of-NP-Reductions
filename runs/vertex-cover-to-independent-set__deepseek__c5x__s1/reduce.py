"""Polynomial-time reduction from Vertex Cover to Independent Set.

Key fact: a set S of vertices is a vertex cover of G = (V, E) if and only if
its complement V \\ S is an independent set of G.  Indeed, S covers every edge
iff no edge has both endpoints outside S, i.e. iff V \\ S contains no edge.

Therefore G has a vertex cover of size AT MOST k iff G has an independent set
of size AT LEAST n - k.  The reduction keeps the graph unchanged and maps the
budget k to n - k.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Map a Vertex Cover instance to an Independent Set instance.

    Input : {"n": n, "edges": [[u, v], ...], "k": k}   (Vertex Cover)
    Output: {"n": n, "edges": [[u, v], ...], "k": n - k} (Independent Set)
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    return {"n": n, "edges": [list(edge) for edge in edges], "k": n - k}
