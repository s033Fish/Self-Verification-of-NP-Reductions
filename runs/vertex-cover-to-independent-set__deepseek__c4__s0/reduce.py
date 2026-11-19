"""Polynomial-time reduction from Vertex Cover to Independent Set.

Key fact: a set S of vertices is a vertex cover of G = (V, E) if and only if
its complement V \\ S is an independent set of G.  Indeed, every edge has an
endpoint in S  <=>  no edge has both endpoints outside S  <=>  V \\ S is
independent.

Therefore G has a vertex cover of size AT MOST k if and only if G has an
independent set of size AT LEAST n - k.  The reduction keeps the same graph
and maps k to n - k.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Vertex Cover instance to an Independent Set instance.

    Instance format (both problems): {"n": n, "edges": [[u, v], ...], "k": k}
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Complement of a vertex cover is an independent set.
    return {"n": n, "edges": [list(edge) for edge in edges], "k": n - k}
