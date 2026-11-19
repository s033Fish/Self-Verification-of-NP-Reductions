"""Polynomial-time reduction from Vertex Cover to Clique.

A set S is a vertex cover of G iff V \\ S is an independent set of G.
An independent set of G is a clique of the complement graph G'.
So G has a vertex cover of size at most k iff G' has a clique of size at
least n - k.
"""

from itertools import combinations


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    present = set()
    for u, v in edges:
        present.add((u, v) if u < v else (v, u))

    complement_edges = [
        [u, v]
        for u, v in combinations(range(n), 2)
        if (u, v) not in present
    ]

    return {"n": n, "edges": complement_edges, "k": n - k}
