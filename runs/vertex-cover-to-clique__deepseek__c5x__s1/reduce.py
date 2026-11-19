"""Polynomial-time reduction from Vertex Cover to Clique.

A set S is a vertex cover of G iff V \\ S is a clique in the complement
graph of G.  Hence G has a vertex cover of size at most k iff the
complement graph has a clique of size at least n - k.
"""

from __future__ import annotations


def reduce(instance: dict) -> dict:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    original = {frozenset((u, v)) for u, v in edges}

    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in original:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": n - k}
