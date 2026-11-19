"""Polynomial-time reduction from Vertex Cover to Dominating Set.

Source instance (Vertex Cover):
    {"n": n, "edges": [[u, v], ...], "k": k}

Target instance (Dominating Set):
    {"n": n, "edges": [[u, v], ...], "k": k}

Construction
------------
Given G = (V, E) with |V| = n, build G' whose vertex set is

    V  union  { w_e : e in E }

(one fresh vertex w_e for every edge e = {u, v}), and whose edge set is

    E  union  { {u, w_e}, {v, w_e} : e = {u, v} in E }.

The original edges of G are kept, and each edge-vertex w_e is joined to both
endpoints of e.

Let iso(G) be the number of isolated vertices of G.  Then

    min dominating set size of G'  =  min vertex cover size of G + iso(G).

Why:
  (<=)  Take a minimum vertex cover C of G (it contains no isolated vertex)
        together with all isolated vertices of G.  Every non-cover vertex has
        a neighbour in C along a kept original edge, every edge-vertex w_e is
        adjacent to an endpoint of e that lies in C, and isolated vertices are
        in the set.  So it is a dominating set of G' of size VC(G) + iso(G).
  (>=)  Any dominating set D of G' must contain every isolated vertex of G
        (they are isolated in G' too).  Let D' = D minus those isolated
        vertices.  For each edge e = {u, v}, the vertex w_e is dominated by
        D', so w_e in D' or u in D' or v in D'.  Start from D' intersect V and,
        for every w_e in D' whose endpoints are both outside D', add one
        endpoint of e.  This is a vertex cover of G of size at most |D'|.
        Hence |D| >= VC(G) + iso(G).

Therefore the target budget is k + iso(G): the target has a dominating set of
size at most k + iso(G) exactly when the source has a vertex cover of size at
most k.  If k < 0 the source is a no-instance, so we use budget -1, which makes
the target a no-instance as well.

The construction uses O(n + |E|) time and space, so it is polynomial.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Vertex Cover instance to an equivalent Dominating Set instance."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    m = len(edges)

    # Count isolated vertices of the source graph.
    degree = [0] * n
    for u, v in edges:
        degree[u] += 1
        degree[v] += 1
    isolated = sum(1 for d in degree if d == 0)

    # Keep every original edge, then attach one fresh vertex per edge to both
    # of its endpoints.  Fresh vertices are numbered n, n+1, ..., n+m-1.
    new_edges: list[list[int]] = [[u, v] for u, v in edges]
    for i, (u, v) in enumerate(edges):
        w = n + i
        new_edges.append([u, w])
        new_edges.append([v, w])

    # k < 0 is a no-instance for the source; keep the target a no-instance.
    new_k = k + isolated if k >= 0 else -1

    return {"n": n + m, "edges": new_edges, "k": new_k}
