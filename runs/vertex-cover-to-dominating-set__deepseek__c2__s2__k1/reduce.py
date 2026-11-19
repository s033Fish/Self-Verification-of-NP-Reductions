"""Polynomial-time reduction from Vertex Cover to Dominating Set.

Source instance (Vertex Cover): {"n": n, "edges": [[u, v], ...], "k": k}
Target instance (Dominating Set): {"n": n, "edges": [[u, v], ...], "k": k}

Construction
------------
Let G = (V, E) be the source graph.  First drop every isolated vertex of G,
obtaining G0 = (V0, E0).  Isolated vertices can never help cover an edge, so
G has a vertex cover of size at most k iff G0 does.

Now build the target graph H as follows:
  * keep every vertex of G0 and every edge of G0;
  * for every edge e = {u, v} in E0 add one fresh vertex w_e and the two
    edges {u, w_e} and {v, w_e}.

The target instance is H with the same budget k.

Correctness
-----------
(=>) If C is a vertex cover of G0 with |C| <= k, then C dominates H:
     every gadget vertex w_e is adjacent to an endpoint of e that lies in C,
     and every non-isolated original vertex x is either in C or adjacent to
     its cover-mate in C.

(<=) If D is a dominating set of H with |D| <= k, replace every gadget
     vertex w_e in D by one of its endpoints.  The resulting set D' is still
     dominating and has |D'| <= |D|.  Since D' contains only original
     vertices, each gadget vertex w_e must be dominated by u or v, so D'
     covers every edge of G0.  Hence D' is a vertex cover of G0 of size <= k.

Therefore the answer is preserved.  The construction is polynomial: it adds
one vertex and two edges per source edge.
"""


def reduce(instance):
    """Return a Dominating Set instance equivalent to the Vertex Cover one."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Degrees in the source graph; isolated vertices (degree 0) are dropped.
    degree = [0] * n
    for u, v in edges:
        degree[u] += 1
        degree[v] += 1

    new_index = {}
    for v in range(n):
        if degree[v] > 0:
            new_index[v] = len(new_index)
    n0 = len(new_index)

    new_edges = []

    # Keep the original edges among the non-isolated vertices.
    for u, v in edges:
        new_edges.append([new_index[u], new_index[v]])

    # One fresh gadget vertex per edge, adjacent to both endpoints.
    for i, (u, v) in enumerate(edges):
        w = n0 + i
        new_edges.append([new_index[u], w])
        new_edges.append([new_index[v], w])

    return {"n": n0 + len(edges), "edges": new_edges, "k": k}
