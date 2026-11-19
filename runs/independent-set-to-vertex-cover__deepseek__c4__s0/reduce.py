"""Polynomial-time reduction from Independent Set to Vertex Cover.

Key fact: a set S of vertices is independent (no edge with both endpoints in S)
iff its complement V \\ S is a vertex cover (every edge has at least one
endpoint outside S, i.e. in V \\ S).

Therefore the graph has an independent set of size >= k iff it has a vertex
cover of size <= n - k.  The reduction keeps the graph and maps k -> n - k.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce an Independent Set instance to a Vertex Cover instance."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    return {"n": n, "edges": [list(e) for e in edges], "k": n - k}
