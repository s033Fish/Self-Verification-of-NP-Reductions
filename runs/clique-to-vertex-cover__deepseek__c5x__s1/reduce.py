r"""Polynomial-time reduction from Clique to Vertex Cover.

Reduction
---------
Let G be the source graph with n vertices and edge set E, and let k be the
source parameter.  Build the complement graph H on the same vertex set:
H has an edge {u, v} (u != v) exactly when {u, v} is NOT an edge of G.
Return the Vertex Cover instance (H, n - k).

Correctness
-----------
A set S of vertices is a clique in G iff every pair of vertices in S is an
edge of G, i.e. iff no pair of vertices in S is an edge of H, i.e. iff the
complement V \ S contains at least one endpoint of every edge of H, i.e. iff
V \ S is a vertex cover of H.

Therefore G has a clique of size >= k
  iff there is a set S with |S| >= k that is a clique in G
  iff there is a vertex cover C = V \ S of H with |C| <= n - k
  iff H has a vertex cover of size at most n - k.

The construction runs in O(n^2) time, so it is polynomial.

Edge cases
----------
* k <= 0: source is yes.  Target parameter n - k >= n, and k' >= n is always
  yes for Vertex Cover (all vertices cover every edge).  Consistent.
* k > n: source is no.  Target parameter n - k < 0, and k' < 0 is always no.
  Consistent.
* k = 1, n >= 1: source is yes.  Target parameter n - 1; any graph on n
  vertices has a vertex cover of size at most n - 1, so the target is yes.
* n = 0: k <= 0 gives source yes and target n - k >= 0 = n, yes; k >= 1
  gives source no and target n - k < 0, no.
"""

from __future__ import annotations

from typing import Any


def _complement_edges(n: int, edges: list[list[int]]) -> list[list[int]]:
    """Return the edges of the complement graph on vertices 0..n-1."""
    present = set()
    for u, v in edges:
        present.add((u, v) if u < v else (v, u))
    complement: list[list[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in present:
                complement.append([u, v])
    return complement


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Clique instance to a Vertex Cover instance.

    The returned instance is yes for Vertex Cover exactly when the input is
    yes for Clique.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    complement = _complement_edges(n, edges)
    return {"n": n, "edges": complement, "k": n - k}
