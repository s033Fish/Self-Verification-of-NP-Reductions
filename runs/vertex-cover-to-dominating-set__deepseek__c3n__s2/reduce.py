"""Polynomial-time reduction: Vertex Cover -> Dominating Set.

Construction (subdivision gadget, keeping the original edges):
    Given G = (V, E) with |V| = n, build G' with
        V' = V  U  { x_e : e in E }
        E' = E  U  { {u, x_e}, {v, x_e} : e = {u, v} in E }
    i.e. every edge of G gets a new subdivision vertex adjacent to both of
    its endpoints, while the original edge is kept.
    Set k' = k + iso(G), where iso(G) is the number of isolated vertices of G.

Correctness:  min DS(G') = min VC(G) + iso(G).

    (<=) Let C be a minimum vertex cover of G (it contains no isolated vertex)
    and let I be the set of isolated vertices.  D = C U I dominates G':
      * each x_e is adjacent to an endpoint of e that lies in C;
      * each v in C is in D;
      * each non-isolated v not in C has an incident edge {v,w} which is
        covered by w in C (as v not in C), and {v,w} is still an edge of G',
        so v is adjacent to w in D;
      * each isolated vertex is in D.
    So DS(G') <= |C| + iso = min VC(G) + iso(G).

    (>=) Let D dominate G'.  Every isolated vertex of G is isolated in G' as
    well, hence lies in D.  The only neighbours of x_e in G' are u and v, so
    for every edge e = {u,v} we have u in D or v in D or x_e in D.  Define
        C = { non-isolated v in D } U { one endpoint of e : x_e in D }.
    Then C is a vertex cover of G and |C| <= |D| - iso(G).  Hence
    min VC(G) <= |D| - iso(G), i.e. |D| >= min VC(G) + iso(G).

    Therefore  VC(G) <= k  <=>  min DS(G') <= k + iso(G)  <=>  DS(G') <= k'.
"""

from __future__ import annotations


def reduce(instance):
    """Reduce a Vertex Cover instance to a Dominating Set instance."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    m = len(edges)

    # Count isolated vertices (degree 0) in the source graph.
    degree = [0] * n
    for u, v in edges:
        degree[u] += 1
        degree[v] += 1
    isolated = sum(1 for d in degree if d == 0)

    # New vertices n, n+1, ..., n+m-1 are the subdivision vertices.
    # Keep the original edges and attach each subdivision vertex to both
    # endpoints of its edge.
    new_edges = [[u, v] for u, v in edges]
    for i, (u, v) in enumerate(edges):
        x = n + i
        new_edges.append([u, x])
        new_edges.append([v, x])

    return {"n": n + m, "edges": new_edges, "k": k + isolated}
