"""Polynomial-time reduction from Vertex Cover to Dominating Set.

Construction
------------
Given a Vertex Cover instance G = (V, E) with |V| = n and k, build a
Dominating Set instance G' as follows:

  * Keep every original vertex 0..n-1 and every original edge.
  * For each edge e_i = (u, v) (i = 0..m-1) add a new vertex w_i = n + i
    and the two edges (u, w_i), (v, w_i).

Set the new budget to k' = k + iso, where iso is the number of isolated
vertices of G (vertices of degree 0).

Correctness
-----------
Let C be a vertex cover of G and Iso the isolated vertices of G.  Then
D = C u Iso dominates G': every original non-isolated vertex is either in
C or adjacent to a cover vertex; every edge-vertex w_i is adjacent to an
endpoint in C; isolated vertices are in D.  Hence
    min_ds(G') <= min_vc(G) + iso.

Conversely, take a minimum dominating set D of G'.  An edge-vertex w_i is
dominated only by itself or by u or v, and replacing w_i by (say) u never
loses domination (the closed neighbourhood of u contains that of w_i).
So we may assume D contains only original vertices.  Every edge-vertex w_i
must then be dominated, i.e. every edge has an endpoint in D, so D is a
vertex cover of G.  Also every isolated vertex v of G is isolated in G'
too, so v must itself be in D.  Therefore D = (vertex cover) u Iso and
    min_ds(G') >= min_vc(G) + iso.

So min_ds(G') = min_vc(G) + iso, and G' has a dominating set of size at
most k' = k + iso iff G has a vertex cover of size at most k.
"""

from __future__ import annotations

from typing import Any

Instance = dict[str, Any]


def reduce(instance: Instance) -> Instance:
    """Map a Vertex Cover instance to a Dominating Set instance."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    degree = [0] * n
    for u, v in edges:
        degree[u] += 1
        degree[v] += 1
    isolated = sum(1 for d in degree if d == 0)

    m = len(edges)
    new_edges: list[list[int]] = [[u, v] for u, v in edges]
    for i, (u, v) in enumerate(edges):
        w = n + i
        new_edges.append([u, w])
        new_edges.append([v, w])

    return {"n": n + m, "edges": new_edges, "k": k + isolated}
