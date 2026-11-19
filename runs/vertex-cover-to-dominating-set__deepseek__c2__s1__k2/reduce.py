"""Polynomial-time reduction from Vertex Cover to Dominating Set.

Source instance:  {"n": n, "edges": [[u, v], ...], "k": k}
Target instance:  {"n": n', "edges": [[u, v], ...], "k": k}

Construction
------------
Let G be the source graph.  Isolated vertices of G never matter for a
vertex cover, so first discard them.  Let A be the set of vertices that
are incident to at least one edge, and let G[A] be the induced subgraph
(which has no isolated vertices).

Relabel A as 0..|A|-1.  Build the target graph H as follows:

  * Keep every edge of G[A] (relabelled).
  * For every edge e = (u, v) of G[A], add a fresh vertex w_e and the
    two edges {u, w_e}, {v, w_e}.  The vertex w_e is adjacent only to u
    and v.

So H has |A| + |E(G[A])| vertices and |E(G[A])| + 2|E(G[A])| edges.

Correctness
-----------
Claim: G has a vertex cover of size at most k iff H has a dominating set
of size at most k.

(=>) Let C be a vertex cover of G[A] with |C| <= k.  Every vertex of A
is either in C or adjacent to a vertex of C (G[A] has no isolated
vertices).  Every gadget vertex w_e is adjacent to the endpoints of e,
and C covers e, so w_e is adjacent to a vertex of C.  Hence C dominates
H.

(<=) Let D be a dominating set of H with |D| <= k.  Build C from D by
keeping the original (A) vertices of D and, for every gadget vertex
w_e in D, replacing it by one endpoint of e.  Then |C| <= |D| <= k.  For
any edge e = (u, v), the vertex w_e is dominated: either w_e is in D
(and we kept an endpoint of e), or one of its only neighbours u, v is in
D.  In both cases C contains u or v, so C is a vertex cover of G[A],
hence of G.

Edge cases: k < 0 gives "no" on both sides.  If G has no edges then A is
empty and H has no vertices, so H has the empty dominating set, matching
the fact that the empty set covers G for every k >= 0.  If k >= n then
selecting all of A (at most n vertices) dominates H, so the target is
also yes.

The construction is linear in the size of the input, hence polynomial.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Vertices that are incident to at least one edge.  Isolated vertices
    # are irrelevant to Vertex Cover and are dropped so that the target
    # graph has no isolated vertices, which the gadget reduction needs.
    active = set()
    for u, v in edges:
        active.add(u)
        active.add(v)

    active = sorted(active)
    index = {v: i for i, v in enumerate(active)}
    m = len(edges)

    new_edges = []

    # Original edges of G[A], relabelled.
    for u, v in edges:
        new_edges.append([index[u], index[v]])

    # One gadget vertex per edge, adjacent to both endpoints.
    for i, (u, v) in enumerate(edges):
        w = len(active) + i
        new_edges.append([index[u], w])
        new_edges.append([index[v], w])

    return {"n": len(active) + m, "edges": new_edges, "k": k}
