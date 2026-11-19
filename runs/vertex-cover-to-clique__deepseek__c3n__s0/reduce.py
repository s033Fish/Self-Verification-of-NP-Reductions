"""Polynomial-time reduction from Vertex Cover to Clique.

Classic complement-graph reduction:

    A set C is a vertex cover of G  <=>  V \\ C is an independent set of G
                                    <=>  V \\ C is a clique of the complement graph.

Hence G has a vertex cover of size AT MOST k
  <=> complement(G) has a clique of size AT LEAST n - k.

So we map (G, k) -> (complement(G), n - k).

Edge cases line up:
  * k < 0: source is no; target k' = n - k > n is no.
  * no edges, k >= 0: complement is K_n, which has a clique of size
    n >= n - k, so yes.
  * k >= n: source is yes; target k' = n - k <= 0 is yes.
"""

from __future__ import annotations


def reduce(instance):
    """Reduce a Vertex Cover instance to a Clique instance."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    present = {frozenset((u, v)) for u, v in edges}

    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in present:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": n - k}
