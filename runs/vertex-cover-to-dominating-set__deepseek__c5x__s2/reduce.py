"""Polynomial-time reduction from Vertex Cover to Dominating Set.

Reduction (standard):
    Given a Vertex Cover instance G = (V, E) with parameter k, build a
    Dominating Set instance G' as follows.

    * Keep every original vertex and every original edge.
    * For every edge e = {u, v} in E, add a new vertex w_e and the two
      edges {u, w_e} and {v, w_e}.

    Let i be the number of isolated vertices of G.  Then

        min vertex cover of G  =  min dominating set of G'  -  i,

    so G has a vertex cover of size at most k iff G' has a dominating set
    of size at most k + i.  We therefore output k' = k + i.

    Why the equality holds:
      * Any dominating set D of G' can be transformed, without growing it,
        into one containing no w_e: if w_e in D and neither endpoint of e is
        in D, replace w_e by one of its endpoints u; u dominates everything
        w_e dominated (u, v, w_e) and more.  Such a D must contain every
        isolated vertex of G, and D ∩ V must contain an endpoint of every
        edge of G, i.e. is a vertex cover.  Hence |D| >= i + minVC(G).
      * Conversely, i isolated vertices plus a minimum vertex cover of G
        dominate all of G' (each w_e is adjacent to a cover vertex), giving
        a dominating set of size i + minVC(G).

The construction uses O(n + m) vertices and O(m) new edges, so it runs in
polynomial time and never calls a solver.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Vertex Cover instance to a Dominating Set instance."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Degree of every original vertex, used to count isolated vertices.
    degree = [0] * n
    for u, v in edges:
        degree[u] += 1
        degree[v] += 1
    isolated = sum(1 for d in degree if d == 0)

    m = len(edges)
    new_n = n + m

    # Original edges are kept; each edge e gets a fresh vertex n + index(e)
    # joined to both of its endpoints.
    new_edges: list[list[int]] = [[u, v] for u, v in edges]
    for index, (u, v) in enumerate(edges):
        w = n + index
        new_edges.append([u, w])
        new_edges.append([v, w])

    return {"n": new_n, "edges": new_edges, "k": k + isolated}
