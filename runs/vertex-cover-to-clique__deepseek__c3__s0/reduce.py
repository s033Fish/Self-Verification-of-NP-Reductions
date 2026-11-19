"""Polynomial-time reduction from Vertex Cover to Clique.

Reduction
---------
Given a Vertex Cover instance (G, k) with n vertices, build the complement
graph G' on the same vertex set 0..n-1, whose edges are exactly the pairs
that are NOT edges of G.  Return the Clique instance (G', n - k).

Correctness
-----------
A set S of vertices is a vertex cover of G (every edge of G has an endpoint
in S) iff its complement V \\ S is an independent set of G (no edge of G has
both endpoints outside S).  An independent set of G is exactly a clique of
the complement graph G'.  Therefore:

    G has a vertex cover of size <= k
    <=> G has an independent set of size >= n - k
    <=> G' has a clique of size >= n - k.

So the source answer is yes iff the target answer is yes.

Edge cases line up with the documented ones:
  * k < 0  -> target k' = n - k > n, and Clique is no for k' > n.
  * k >= n -> target k' = n - k <= 0, and Clique is yes for k' <= 0.
  * no edges -> G' is complete, which has a clique of size n, so the target
    is yes exactly when n - k <= n, i.e. k >= 0.
  * n = 0  -> G' has no vertices; target yes iff k' <= 0 iff k >= 0.

The construction runs in O(n^2) time, which is polynomial in the encoding
length of the instance.
"""

from __future__ import annotations

from itertools import combinations
from typing import Any

Instance = dict[str, Any]


def reduce(instance: Instance) -> Instance:
    """Reduce a Vertex Cover instance to an equivalent Clique instance."""
    n = instance["n"]
    k = instance["k"]

    # Set of undirected edges of the source graph, orientation-independent.
    source_edges = {frozenset(edge) for edge in instance["edges"]}

    # Complement graph: keep every pair that is not a source edge.
    complement_edges = [
        [u, v]
        for u, v in combinations(range(n), 2)
        if frozenset((u, v)) not in source_edges
    ]

    return {"n": n, "edges": complement_edges, "k": n - k}
