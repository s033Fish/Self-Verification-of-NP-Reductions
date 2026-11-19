"""Polynomial-time reduction from Clique to Vertex Cover.

A clique in G is exactly an independent set in the complement graph G'.
The complement of an independent set is a vertex cover, so:

    G has a clique of size >= k
    <=> G' has an independent set of size >= k
    <=> G' has a vertex cover of size <= n - k.

Hence we map (G, k) to (G', n - k), where G' is the complement of G.
This is a valid reduction for all integers k, including the edge cases:
  * k <= 0: source yes; target k' = n - k >= n, and Vertex Cover is yes
    for any k' >= n.
  * k > n: source no; target k' = n - k < 0, and Vertex Cover is no for
    any k' < 0.
"""

from itertools import combinations


def _complement_edges(n, edges):
    """Edge list of the complement graph on vertices 0..n-1."""
    present = set()
    for u, v in edges:
        present.add((u, v) if u < v else (v, u))
    return [[u, v] for u, v in combinations(range(n), 2) if (u, v) not in present]


def reduce(instance):
    """Reduce a Clique instance to a Vertex Cover instance."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    return {"n": n, "edges": _complement_edges(n, edges), "k": n - k}
