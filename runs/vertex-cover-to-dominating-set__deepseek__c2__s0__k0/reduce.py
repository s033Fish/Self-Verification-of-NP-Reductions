"""Polynomial-time reduction from Vertex Cover to Dominating Set.

Source instance (Vertex Cover):
    {"n": n, "edges": [[u, v], ...], "k": k}

Target instance (Dominating Set):
    {"n": n', "edges": [[u, v], ...], "k": k'}

Construction
------------
Let G = (V, E) be the source graph and let I be the set of isolated
vertices of G (vertices of degree 0).  Build G' = (V', E') as follows:

  * Keep every original vertex and every original edge of G.
  * For every edge e = {u, v} in E, add one brand-new vertex w_e and the
    two edges {u, w_e} and {v, w_e}.

So each original edge is turned into a triangle u - v - w_e, and
n' = n + |E|.  Set k' = k + |I|.

Why the original edges are kept
-------------------------------
If they were dropped (plain subdivision), a non-isolated vertex u not in
the cover would only be adjacent to the new w_e vertices and could not be
dominated by the cover.  Keeping {u, v} lets a vertex cover dominate all
original vertices as well.

Correctness
-----------
Claim: min dominating set size of G' = min vertex cover size of G + |I|.

(VC -> DS)  Let C be a vertex cover of G with |C| <= k and put
    D = C union I.  Every isolated vertex is in D.  If u is a
    non-isolated vertex with u not in C, then every edge incident to u
    has its other endpoint in C, so u is adjacent to a member of C and
    is dominated.  Each new vertex w_e is adjacent to the endpoints of
    e, at least one of which lies in C.  Hence D dominates G' and
    |D| <= k + |I|.

(DS -> VC)  Let D be a dominating set of G'.  Every isolated vertex of
    G is isolated in G' as well, so I is contained in D.  Put
    D' = D \ I.  For an edge e = {u, v}, the new vertex w_e is adjacent
    only to u and v, so w_e is dominated by D' only if u in D', v in D',
    or w_e in D'.  Build C from D' by keeping every original vertex of
    D' and, for every new vertex w_e in D', adding one endpoint of e.
    Then C covers every edge of G and |C| <= |D'| = |D| - |I|.  Hence
    |D| >= (min vertex cover of G) + |I|.

Therefore G has a vertex cover of size at most k exactly when G' has a
dominating set of size at most k + |I|.

The construction runs in time O(n + |E|), hence in polynomial time, and
it never invokes a solver.
"""


def reduce(instance):
    """Reduce a Vertex Cover instance to a Dominating Set instance."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Count isolated vertices of the source graph.
    degree = [0] * n
    for u, v in edges:
        degree[u] += 1
        degree[v] += 1
    isolated = sum(1 for d in degree if d == 0)

    # Keep all original edges and add one fresh vertex per edge, adjacent
    # to both endpoints of that edge.
    new_edges = []
    next_vertex = n
    for u, v in edges:
        w = next_vertex
        next_vertex += 1
        new_edges.append([u, v])   # original edge is kept
        new_edges.append([u, w])
        new_edges.append([v, w])

    return {"n": next_vertex, "edges": new_edges, "k": k + isolated}
