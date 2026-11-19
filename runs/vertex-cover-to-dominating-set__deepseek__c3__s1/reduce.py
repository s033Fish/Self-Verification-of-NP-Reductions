"""Polynomial-time reduction from Vertex Cover to Dominating Set.

Source instance: {"n": n, "edges": [[u, v], ...], "k": k}  (Vertex Cover)
Target instance: {"n": n, "edges": [[u, v], ...], "k": k}  (Dominating Set)

Construction
------------
Given a Vertex Cover instance G = (V, E) with |V| = n and |E| = m, build a
Dominating Set instance G' as follows:

  * Keep every original vertex 0..n-1 and every original edge of G.
  * For each edge e_i = (u, v) add a fresh vertex w_i (numbered n + i) and
    the two edges (u, w_i) and (v, w_i).  So w_i is adjacent exactly to the
    two endpoints of e_i (plus the original edges remain).
  * Let iso be the number of isolated vertices of G (degree 0).  Set the new
    budget k' = k + iso.

Correctness
-----------
Every fresh vertex w_i has degree 2 (u != v), so the isolated vertices of G'
are exactly the isolated vertices of G.

(=>) If C is a vertex cover of G with |C| <= k, then C together with all
isolated vertices of G dominates G':
  - each gadget vertex w_i is adjacent to an endpoint of e_i that lies in C;
  - each non-isolated original vertex v is either in C, or (v not in C) every
    edge incident to v has its other endpoint in C, and v has an incident
    edge, so v is adjacent (via an original edge) to a vertex of C;
  - isolated vertices are included.
  Size <= k + iso = k'.

(<=) If D dominates G' with |D| <= k', then D must contain all iso isolated
vertices.  Let D' = D minus those, so |D'| <= k.  Build C from D' by keeping
the original vertices and, for every gadget vertex w_i in D', replacing it by
one of its endpoints u or v.  Then |C| <= |D'| <= k.  For every edge
e_i = (u, v) of G, the gadget vertex w_i is dominated by D, so either
w_i in D (and we put an endpoint of e_i into C) or u or v lies in D (and
hence in C).  Thus C is a vertex cover of G of size <= k.

Hence G has a vertex cover of size at most k iff G' has a dominating set of
size at most k'.  The construction is clearly polynomial.

Edge cases
----------
k < 0: the source answer is always no, so return the trivially-no target
instance {"n": 0, "edges": [], "k": -1} (a negative budget is always no).
"""

from __future__ import annotations

from typing import Any

Instance = dict[str, Any]


def reduce(instance: Instance) -> Instance:
    """Reduce a Vertex Cover instance to a Dominating Set instance."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # k < 0 is always no for Vertex Cover; map to an always-no target.
    if k < 0:
        return {"n": 0, "edges": [], "k": -1}

    # Count isolated vertices of the source graph.
    degree = [0] * n
    for u, v in edges:
        degree[u] += 1
        degree[v] += 1
    iso = sum(1 for d in degree if d == 0)

    # Keep original edges and add one gadget vertex per edge.
    new_edges: list[list[int]] = [[u, v] for u, v in edges]
    for i, (u, v) in enumerate(edges):
        w = n + i
        new_edges.append([u, w])
        new_edges.append([v, w])

    return {"n": n + len(edges), "edges": new_edges, "k": k + iso}
