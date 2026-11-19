"""Polynomial-time reduction from Vertex Cover to Clique.

Reduction
---------
Given a Vertex Cover instance (G, k), build the complement graph G' on the
same vertex set and ask for a clique of size at least n - k.

Correctness
-----------
A set S is a vertex cover of G  iff  V \\ S is an independent set in G
iff  V \\ S is a clique in the complement graph G'.  Moreover |S| <= k
iff |V \\ S| >= n - k.  Hence G has a vertex cover of size at most k iff
G' has a clique of size at least n - k.

Edge cases
----------
* k < 0: source is no; target k' = n - k > n is no.
* no edges: source is yes for k >= 0; G' is complete, which has a clique of
  size n >= n - k for every k >= 0.
* k >= n: source is yes; target k' = n - k <= 0 is always yes.

The reduction runs in O(n^2) time.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Vertex Cover instance to a Clique instance."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    present = set()
    for u, v in edges:
        present.add((u, v) if u < v else (v, u))

    complement = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in present:
                complement.append([u, v])

    return {"n": n, "edges": complement, "k": n - k}
