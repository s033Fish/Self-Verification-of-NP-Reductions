"""Polynomial-time reduction from Vertex Cover to Dominating Set.

Construction
------------
Given a Vertex Cover instance G = (V, E) with budget k:

1. Let V' be the set of *non-isolated* vertices of G (vertices incident to at
   least one edge).  Isolated vertices are dropped: they never help cover an
   edge, so VC(G) = VC(G[V']).
2. Keep every original edge between vertices of V'.
3. For every edge e = {u, v} add a fresh gadget vertex w_e adjacent to both u
   and v.

The resulting graph G' has |V'| + |E| vertices.

Correctness: DS(G') = VC(G).
  (<=) A vertex cover C of G (restricted to V') dominates G': every vertex of
       V' is either in C or adjacent (via an original edge) to a vertex of C,
       and each gadget w_e is adjacent to an endpoint of e that lies in C.
  (>=) In any dominating set D we may replace a gadget vertex w_e by one of its
       endpoints u without losing domination (u dominates u, v and w_e).  Then
       D is a vertex cover of G: the gadget w_e must be dominated, so one of its
       endpoints u, v lies in D.  Hence |D| >= VC(G).

So G has a vertex cover of size at most k iff G' has a dominating set of size
at most k.  The construction runs in polynomial time.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Vertex Cover instance to a Dominating Set instance."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Vertices that are incident to at least one edge.
    non_isolated: set[int] = set()
    for u, v in edges:
        non_isolated.add(u)
        non_isolated.add(v)

    # Relabel non-isolated vertices to 0..m-1.
    mapping = {v: i for i, v in enumerate(sorted(non_isolated))}
    m = len(mapping)

    new_edges: list[list[int]] = []

    # Original edges, relabelled.
    for u, v in edges:
        new_edges.append([mapping[u], mapping[v]])

    # One gadget vertex per edge, adjacent to both endpoints.
    for i, (u, v) in enumerate(edges):
        gadget = m + i
        new_edges.append([mapping[u], gadget])
        new_edges.append([mapping[v], gadget])

    return {"n": m + len(edges), "edges": new_edges, "k": k}
