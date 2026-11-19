"""Polynomial-time reduction from Vertex Cover to Clique.

A set S is a vertex cover of G iff V \\ S is an independent set of G.
An independent set in G is a clique in the complement graph G'.
Therefore G has a vertex cover of size at most k iff the complement graph
has a clique of size at least n - k.

So the reduction keeps the same vertex set, replaces the edge set with its
complement, and maps k -> n - k.
"""

from __future__ import annotations


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Set of original undirected edges (normalized to u < v).
    original = set()
    for u, v in edges:
        if u > v:
            u, v = v, u
        original.add((u, v))

    # Complement graph: all pairs not present in the original graph.
    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in original:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": n - k}
