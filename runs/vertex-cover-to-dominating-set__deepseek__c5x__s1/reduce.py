"""Polynomial-time reduction from Vertex Cover to Dominating Set.

Construction
------------
Given a Vertex Cover instance G = (V, E) with |V| = n and |E| = m, build a
Dominating Set instance G' = (V', E') as follows:

    V' = V  union  { w_e : e in E }        (one fresh vertex per edge)
    E' = E  union  { (u, w_e), (v, w_e) : e = (u, v) in E }

so |V'| = n + m.  Set

    k' = k + iso(G),

where iso(G) is the number of isolated vertices of G (vertices of degree 0).

Correctness
-----------
Let I be the set of isolated vertices of G.

(<=) If C is a vertex cover of G, then D = C union I is a dominating set of G':
     * each fresh vertex w_e (e = (u,v)) is adjacent to u and v, and C covers e,
       so u in C or v in C, hence w_e is dominated;
     * each non-isolated v in V either lies in C, or every incident edge (v,u)
       has u in C, so v is adjacent to a member of C;
     * each isolated v lies in I, hence in D.
     So |D| = |C| + |I|.

(=>) If D is a dominating set of G', then:
     * every isolated vertex of G is isolated in G' too, so it must belong to D;
       hence I subset D.
     * for every edge e = (u,v) of G, the fresh vertex w_e has neighbourhood
       exactly {u, v}, so u in D or v in D; thus D ∩ V is a vertex cover of G.
     Therefore |D| >= |D ∩ V| >= min-vertex-cover-size-containing-I
                     = vc(G) + |I|.

Consequently the minimum dominating set of G' has size exactly vc(G) + |I|, so

    G' has a dominating set of size <= k' = k + |I|
        <=>  vc(G) + |I| <= k + |I|
        <=>  vc(G) <= k
        <=>  G has a vertex cover of size <= k.

This also handles the edge cases: k < 0 gives k' = k + |I| and vc(G)+|I| > k+|I|,
so both answers are "no"; n = 0 has no isolated vertices and the construction is
the identity on k.  The construction is clearly polynomial (O(n + m) time and
space).
"""

from __future__ import annotations


def reduce(instance: dict) -> dict:
    """Reduce a Vertex Cover instance to a Dominating Set instance."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    degree = [0] * n
    for u, v in edges:
        degree[u] += 1
        degree[v] += 1
    isolated = sum(1 for d in degree if d == 0)

    new_edges = [[u, v] for u, v in edges]
    for i, (u, v) in enumerate(edges):
        w = n + i
        new_edges.append([u, w])
        new_edges.append([v, w])

    return {"n": n + len(edges), "edges": new_edges, "k": k + isolated}
