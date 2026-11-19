"""Polynomial-time reduction from Vertex Cover to Dominating Set.

Construction
------------
Let G = (V, E) be the source graph and k the budget.

1. Drop every isolated vertex of G.  Isolated vertices are irrelevant to a
   vertex cover, so the minimum vertex-cover size is unchanged.  Renumber the
   remaining vertices 0..n2-1; call the resulting graph H.

2. Build the standard edge-vertex gadget for H: for every edge e = {u, v} of
   H add a fresh vertex x_e joined to both u and v.

Claim: H has a vertex cover of size <= k iff the constructed graph G' has a
dominating set of size <= k.

(=>) A vertex cover C of H dominates every vertex of H: each vertex has an
incident edge, and C covers that edge (if the vertex itself is not in C, the
other endpoint is, and it is adjacent).  C also dominates every gadget vertex
x_e, because x_e is adjacent to both endpoints of e and C contains one of
them.  So C is a dominating set of G'.

(<=) Given a dominating set D of G', replace each gadget vertex x_e in D by
one of its endpoints.  This cannot lose domination (that endpoint dominates
x_e and everything x_e dominated), so we obtain a set D' of H-vertices with
|D'| <= |D|.  Every gadget vertex x_e must be dominated by D', hence one of
its endpoints lies in D', i.e. D' covers every edge of H.  Thus D' is a
vertex cover of H.

The reduction runs in O(n + m) time and uses O(n + m) space.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Degrees in the source graph, used to detect isolated vertices.
    degree = [0] * n
    for u, v in edges:
        degree[u] += 1
        degree[v] += 1

    # Keep only non-isolated vertices and renumber them 0..n2-1.
    keep = [v for v in range(n) if degree[v] > 0]
    index = {v: i for i, v in enumerate(keep)}
    n2 = len(keep)

    base_edges = [[index[u], index[v]] for u, v in edges]
    m = len(base_edges)

    # Add one fresh gadget vertex per edge, adjacent to both endpoints.
    new_edges = list(base_edges)
    for i, (u, v) in enumerate(base_edges):
        w = n2 + i
        new_edges.append([u, w])
        new_edges.append([v, w])

    return {"n": n2 + m, "edges": new_edges, "k": k}
