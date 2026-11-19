"""Polynomial-time reduction from Clique to Independent Set.

A set S of vertices is a clique in G iff S is an independent set in the
complement graph G'.  Therefore a clique of size >= k exists in G iff an
independent set of size >= k exists in G'.  We keep n and k unchanged and
replace the edge list by the list of non-edges of G.

The construction takes O(n^2) time, which is polynomial in the input size.
"""

from __future__ import annotations


def reduce(instance: dict) -> dict:
    """Map a Clique instance to an Independent Set instance.

    Input : {"n": n, "edges": [[u, v], ...], "k": k}
    Output: {"n": n, "edges": [[u, v], ...], "k": k}
            where the output edges are exactly the non-edges of the input
            graph (the complement graph).
    """
    n = instance["n"]
    edges = instance["edges"]

    edge_set = set()
    for u, v in edges:
        edge_set.add(frozenset((u, v)))

    complement = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in edge_set:
                complement.append([u, v])

    return {"n": n, "edges": complement, "k": instance["k"]}
