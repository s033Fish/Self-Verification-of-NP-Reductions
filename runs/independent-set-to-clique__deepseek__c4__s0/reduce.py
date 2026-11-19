"""Polynomial-time reduction from Independent Set to Clique.

An independent set in a graph G is exactly a clique in the complement graph
G'.  So we map {"n": n, "edges": E, "k": k} to {"n": n, "edges": E', "k": k}
where E' contains every unordered pair {u, v} (u != v) that is NOT in E.
The number of vertices and the threshold k are unchanged, so the yes/no
answer is preserved (including the k <= 0 and k > n edge cases).
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]

    present: set[frozenset[int]] = set()
    for u, v in edges:
        present.add(frozenset((u, v)))

    complement: list[list[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in present:
                complement.append([u, v])

    return {"n": n, "edges": complement, "k": instance["k"]}
