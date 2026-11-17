"""Polynomial-time reduction from Clique to Independent Set.

A clique in G is exactly an independent set in the complement graph G'.
So the reduction maps an instance (n, edges, k) of Clique to the instance
(n, complement_edges, k) of Independent Set.  Building the complement takes
O(n^2) time, which is polynomial in the instance size.
"""

from itertools import combinations


def _complement_edges(n, edges):
    """Return the edge list of the complement of the graph on 0..n-1."""
    present = set()
    for u, v in edges:
        present.add((u, v) if u < v else (v, u))
    complement = []
    for u, v in combinations(range(n), 2):
        if (u, v) not in present:
            complement.append([u, v])
    return complement


def reduce(instance):
    """Reduce a Clique instance to an Independent Set instance.

    Input/output format: {"n": n, "edges": [[u, v], ...], "k": k}.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    return {"n": n, "edges": _complement_edges(n, edges), "k": k}
