"""Polynomial-time reduction from Vertex Cover to Independent Set.

A set S is a vertex cover of G iff V \\ S is an independent set of G.
Therefore G has a vertex cover of size AT MOST k iff G has an independent
set of size AT LEAST n - k.  So the reduction keeps the same graph and maps
k -> n - k.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Vertex Cover instance to an Independent Set instance."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    return {"n": n, "edges": [list(edge) for edge in edges], "k": n - k}
