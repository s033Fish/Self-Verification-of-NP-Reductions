"""Polynomial-time reduction from Independent Set to Vertex Cover.

Key fact: a set S of vertices is independent in G if and only if its
complement V \\ S is a vertex cover of G.  Therefore G has an independent
set of size >= k iff G has a vertex cover of size <= n - k.

So the reduction keeps the same graph and maps k -> n - k.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    # Same graph; independent set of size >= k <=> vertex cover of size <= n-k.
    return {"n": n, "edges": [list(e) for e in edges], "k": n - k}
