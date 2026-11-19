"""Polynomial-time reduction from Vertex Cover to Dominating Set.

Reduction
---------
Given a Vertex Cover instance G = (V, E) with budget k, build a Dominating
Set instance G' as follows:

  * Keep every vertex of G (vertices 0..n-1).
  * For every edge e_i = (u, v) of G add one fresh vertex w_i and the two
    edges {u, w_i} and {v, w_i}.
  * Let m be the number of isolated vertices of G (degree 0).
  * Set the new budget to k' = k + m.

Why it is correct
-----------------
(=>) Let C be a vertex cover of G with |C| <= k.  Then D = C together with
all isolated vertices of G has size <= k + m.  Every edge-gadget vertex w_i
is adjacent to u or v, one of which lies in C, so it is dominated.  Every
non-isolated original vertex x not in D has an incident edge (x, y); since C
is a vertex cover, y in C, so x is dominated.  Isolated vertices are in D.
Hence D is a dominating set of G' of size <= k + m.

(<=) Let D be a dominating set of G' with |D| <= K.  Every isolated vertex
of G has only itself as a closed neighbour, so it belongs to D.  Replace each
gadget vertex w_i in D by one of its two endpoints (say u).  The resulting
set D' contains only original vertices, has |D'| <= |D|, and still contains
all isolated vertices.  For every edge (u, v) of G, the gadget vertex w_i was
dominated by D, so after the replacement at least one of u, v lies in D';
thus D' is a vertex cover of G.  Therefore G has a vertex cover containing
all isolated vertices of size <= K, i.e. a vertex cover of size <= K - m.

Taking K = k + m gives: G' has a dominating set of size <= k + m iff G has a
vertex cover of size <= k.

The construction adds exactly one vertex and two edges per edge of G, so it
runs in O(n + |E|) time.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict) -> dict:
    """Reduce a Vertex Cover instance to a Dominating Set instance."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    degree = [0] * n
    for u, v in edges:
        degree[u] += 1
        degree[v] += 1
    isolated = sum(1 for d in degree if d == 0)

    new_n = n + len(edges)
    new_edges: list[list[int]] = [list(edge) for edge in edges]
    for i, (u, v) in enumerate(edges):
        gadget = n + i
        new_edges.append([u, gadget])
        new_edges.append([v, gadget])

    return {"n": new_n, "edges": new_edges, "k": k + isolated}
