"""Polynomial-time reduction from Vertex Cover to Dominating Set.

Construction
------------
Given a Vertex Cover instance G = (V, E) with |V| = n and integer k, build a
Dominating Set instance G' as follows:

  * Keep every original vertex 0..n-1.
  * For each edge e_i = (u, v) (using its index i in the edge list) add one
    new vertex n + i and the two edges {u, n+i} and {v, n+i}.

Let ``iso`` be the number of isolated vertices of G (vertices of degree 0).
The target budget is ``k + iso`` (or -1 when k < 0, since the source is then
a definite no).

Correctness
-----------
Every isolated vertex of G is isolated in G' too, so it must belong to any
dominating set of G'.  For an edge e = (u, v) of G, the only neighbours of the
new vertex w_e are u and v, so any dominating set of G' contains u or v: the
non-isolated part of a dominating set is a vertex cover of G.  Conversely, a
vertex cover C of G together with all isolated vertices of G dominates G':
every edge-vertex w_e has an endpoint in C, every non-isolated original vertex
has an incident edge whose other endpoint lies in C, and every isolated vertex
is included explicitly.  Hence

    min dominating set of G' = iso + (min vertex cover of G),

and therefore G has a vertex cover of size at most k iff G' has a dominating
set of size at most k + iso.  The construction runs in linear time.
"""


def reduce(instance):
    """Map a Vertex Cover instance to a Dominating Set instance."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    new_edges = []
    degree = [0] * n
    for i, (u, v) in enumerate(edges):
        new_edges.append([u, v])
        w = n + i
        new_edges.append([u, w])
        new_edges.append([v, w])
        degree[u] += 1
        degree[v] += 1

    isolated = sum(1 for d in degree if d == 0)

    new_k = -1 if k < 0 else k + isolated

    return {"n": n + len(edges), "edges": new_edges, "k": new_k}
