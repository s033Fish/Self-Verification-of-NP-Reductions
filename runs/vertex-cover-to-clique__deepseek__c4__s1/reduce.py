r"""Polynomial-time reduction from Vertex Cover to Clique.

A set S is a vertex cover of G = (V, E) iff V \ S is a clique in the
complement graph G'.  Hence G has a vertex cover of size at most k iff the
complement graph has a clique of size at least n - k.

So the reduction maps {"n": n, "edges": E, "k": k} to
{"n": n, "edges": complement(E), "k": n - k}.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    present = set()
    for u, v in edges:
        present.add((u, v) if u < v else (v, u))

    complement = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in present:
                complement.append([u, v])

    return {"n": n, "edges": complement, "k": n - k}
