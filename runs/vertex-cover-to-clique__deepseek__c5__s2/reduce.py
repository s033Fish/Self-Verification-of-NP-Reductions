"""Polynomial-time reduction from Vertex Cover to Clique.

Reduction
---------
Let G = (V, E) be the source graph with |V| = n and let k be the source
budget.  Build the complement graph G' = (V, E') on the same vertex set,
where {u, v} is an edge of G' exactly when {u, v} is NOT an edge of G
(u != v).  Return the Clique instance (G', n - k).

Correctness
-----------
A set S is a vertex cover of G iff V minus S is an independent set of G, which
iff V minus S is a clique of G'.  Hence:

    G has a vertex cover of size <= k
      <=> G has an independent set of size >= n - k
      <=> G' has a clique of size >= n - k.

So the source answer is yes exactly when the returned Clique instance
(with target k' = n - k) is yes.

Edge cases line up as well:
  * k < 0: source is no; target k' = n - k > n, and k' > n is always no.
  * k >= n: source is yes; target k' = n - k <= 0, and k' <= 0 is always yes.
  * no edges, k >= 0: source is yes; G' is the complete graph K_n, which has
    a clique of size n >= n - k, so target is yes.

The reduction runs in O(n^2) time and uses O(n^2) space, so it is
polynomial.  It never calls a brute-force solver.
"""

from __future__ import annotations

from problems import SOURCE, TARGET


def reduce(instance: dict) -> dict:
    """Reduce a Vertex Cover instance to a Clique instance."""
    SOURCE.validate(instance)

    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    original = {frozenset((u, v)) for u, v in edges}

    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in original:
                complement_edges.append([u, v])

    result = {"n": n, "edges": complement_edges, "k": n - k}
    TARGET.validate(result)
    return result
