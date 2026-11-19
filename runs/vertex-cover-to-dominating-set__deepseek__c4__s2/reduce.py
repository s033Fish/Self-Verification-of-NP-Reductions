"""Polynomial-time reduction from Vertex Cover to Dominating Set.

Construction
------------
Given a Vertex Cover instance G = (V, E) with n = |V| and m = |E|, build a
Dominating Set instance G' as follows:

  * Keep the whole original graph G (all n vertices and all m edges).
  * For each edge e_j = (u, v) of G (j = 0..m-1) add a fresh vertex
    w_j = n + j, joined to both u and v.

So G' has n + m vertices and m + 2m = 3m edges.

Why it works
------------
Let I be the number of isolated vertices of G.

(<=) If C is a minimum vertex cover of G, then D = C union {isolated vertices}
     is a dominating set of G':
       - an isolated original vertex is in D;
       - a non-isolated original vertex v: if v in C it is in D, otherwise
         every incident edge is covered by C, so some neighbour of v lies in C;
       - a fresh vertex w_j is adjacent to the endpoints of e_j, and C covers
         e_j, so w_j is dominated.
     Hence minDS(G') <= minVC(G) + I.

(>=) Let D be any dominating set of G' and put S = D intersect V,
     T = D intersect {w_j}.  Let U be the set of edges of G not covered by S.
     For each e in U, its fresh vertex w_e must be dominated, and neither
     endpoint of e is in S, so w_e in T; hence |T| >= |U|.  Also every
     isolated vertex of G lies in S (it has no neighbours and no incident
     edges in G').  Now C = S union {one endpoint of each edge in U} is a
     vertex cover of G that contains all isolated vertices, so
        |C| = |S| + |U| <= |S| + |T| = |D|,
     and |C| >= minVC(G) + I (isolated vertices are in no edge, so a minimum
     vertex cover that contains all of them has size minVC(G) + I).
     Hence |D| >= minVC(G) + I.

Therefore minDS(G') = minVC(G) + I, and G has a vertex cover of size at most
k iff G' has a dominating set of size at most k + I.  The construction is
polynomial (O(n + m) time and space).
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Vertex Cover instance to a Dominating Set instance."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    degree = [0] * n
    for u, v in edges:
        degree[u] += 1
        degree[v] += 1
    isolated = sum(1 for d in degree if d == 0)

    # Keep every original edge, and add a fresh vertex per edge joined to both
    # endpoints.
    new_edges: list[list[int]] = [list(edge) for edge in edges]
    for j, (u, v) in enumerate(edges):
        w = n + j
        new_edges.append([u, w])
        new_edges.append([v, w])

    return {"n": n + len(edges), "edges": new_edges, "k": k + isolated}
