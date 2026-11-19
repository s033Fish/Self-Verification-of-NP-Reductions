"""Polynomial-time reduction from Vertex Cover to Dominating Set.

Construction
------------
Given a Vertex Cover instance G = (V, E) with parameter k:

1. Discard every isolated vertex of G (a vertex incident to no edge).  Such
   vertices are irrelevant to vertex covers, but in a dominating set they
   would have to be selected themselves, which would corrupt the parameter.
2. Keep all original edges.
3. For every edge {u, v} of G add a new "subdivision" vertex w together with
   the edges {u, w} and {w, v}.

The resulting graph H has a dominating set of size at most k if and only if G
has a vertex cover of size at most k.

Correctness
-----------
(=>) Let C be a vertex cover of G with |C| <= k.  Drop from C any isolated
vertices; the result C' is still a vertex cover with |C'| <= k and contains
only non-isolated vertices, i.e. vertices of H.  Every non-isolated vertex v
not in C' has a neighbour u with {u, v} an edge of G, and that edge must be
covered by C', so u in C'; since the original edge {u, v} is present in H, v
is dominated.  Every subdivision vertex w_{uv} is adjacent to u and v, at
least one of which lies in C'.  So C' dominates H.

(<=) Let D be a dominating set of H with |D| <= k.  Each subdivision vertex
w_{uv} is dominated, so w_{uv} in D or u in D or v in D.  Replacing every
subdivision vertex w_{uv} in D by one of its endpoints u yields a set D' with
|D'| <= |D| <= k (the closed neighbourhood of w_{uv} is contained in that of
u) that contains no subdivision vertices and still dominates H.  In
particular every subdivision vertex w_{uv} is dominated by D', and since D'
contains no subdivision vertex it must contain u or v.  Hence for every edge
{u, v} of G at least one endpoint is in D': D' is a vertex cover of G.

The construction is clearly polynomial (linear) in the input size.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Vertex Cover instance to a Dominating Set instance."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Degree of every vertex, used to detect isolated vertices.
    degree = [0] * n
    for u, v in edges:
        degree[u] += 1
        degree[v] += 1

    # Compact ids for the non-isolated original vertices: 0 .. m-1.
    new_id = [-1] * n
    m = 0
    for v in range(n):
        if degree[v] > 0:
            new_id[v] = m
            m += 1

    # Keep the original edges and subdivide every edge.  Subdivision vertices
    # get ids m, m+1, ...
    new_edges: list[list[int]] = []
    for i, (u, v) in enumerate(edges):
        a = new_id[u]
        b = new_id[v]
        w = m + i
        new_edges.append([a, b])
        new_edges.append([a, w])
        new_edges.append([w, b])

    return {"n": m + len(edges), "edges": new_edges, "k": k}
