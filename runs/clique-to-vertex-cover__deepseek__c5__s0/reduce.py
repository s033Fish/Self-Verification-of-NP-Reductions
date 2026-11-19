r"""Polynomial-time reduction from Clique to Vertex Cover.

Key fact: S is a clique in G  <=>  S is an independent set in the complement
graph G'.  And I is an independent set in a graph H  <=>  V(H) \ I is a
vertex cover of H.  Therefore:

    G has a clique of size >= k
      <=> G' has an independent set of size >= k
      <=> G' has a vertex cover of size <= n - k.

So the reduction keeps n, replaces edges by their complement, and maps
k -> n - k.  It runs in O(n^2) time.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Clique instance to a Vertex Cover instance.

    Input:  {"n": n, "edges": [[u, v], ...], "k": k}   (Clique)
    Output: {"n": n, "edges": [[u, v], ...], "k": n - k} (Vertex Cover)
    where the output edges are exactly the non-edges of the input graph.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Canonical set of undirected edges of the input graph.
    present = set()
    for u, v in edges:
        present.add((u, v) if u < v else (v, u))

    # Complement edges: every pair {u, v} with 0 <= u < v < n not present.
    complement = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in present:
                complement.append([u, v])

    return {"n": n, "edges": complement, "k": n - k}
