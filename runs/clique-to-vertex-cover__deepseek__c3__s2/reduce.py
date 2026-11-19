"""Polynomial-time reduction from Clique to Vertex Cover.

Given a Clique instance (G, k), build the complement graph G' on the same
vertex set and ask for a vertex cover of size at most n - k.

Correctness: a set C is a clique in G iff C is an independent set in the
complement G'.  A set S is a vertex cover of G' iff its complement V \\ S is
an independent set of G'.  Hence G has a clique of size >= k iff G' has a
vertex cover of size <= n - k.  The construction takes O(n^2) time.
"""

from itertools import combinations


def _complement_edges(n, edges):
    present = set()
    for u, v in edges:
        present.add((u, v) if u < v else (v, u))
    return [[u, v] for u, v in combinations(range(n), 2) if (u, v) not in present]


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    return {"n": n, "edges": _complement_edges(n, edges), "k": n - k}
