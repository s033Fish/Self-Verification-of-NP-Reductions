"""Polynomial-time reduction from Vertex Cover to Dominating Set.

Source instance format (Vertex Cover):
    {"n": n, "edges": [[u, v], ...], "k": k}

Target instance format (Dominating Set):
    {"n": n, "edges": [[u, v], ...], "k": k}

Construction
------------
Let G be the source graph and let V' be the set of non-isolated vertices of G.
Isolated vertices never belong to a minimum vertex cover, so we omit them.

Build a target graph H as follows:
  * Keep one vertex for every vertex in V'.
  * Add one new gadget vertex g_e for every edge e = (u, v) of G.
  * Keep every original edge (u, v) between vertices of V'.
  * Add the two edges (u, g_e) and (v, g_e).

Set H's k equal to the source k.

Correctness
-----------
Every vertex cover C of G is a dominating set of H: vertices of V' not in C
have a neighbour in C (they are non-isolated and C covers all incident edges),
and each g_e is adjacent to an endpoint in C.

Conversely, take a minimum dominating set D of H.  If D contains a gadget
vertex g_e but neither endpoint of e, replace g_e by one endpoint of e; this
keeps D dominating and does not increase its size.  Repeating gives a
dominating set D' of the same or smaller size that contains no gadget
vertices.  For each edge e = (u, v), g_e must be dominated, so u or v lies in
D'.  Hence D' is a vertex cover of G.  Therefore min dominating set size of H
equals min vertex cover size of G, and the answers are identical.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Degrees are used only to detect isolated vertices.
    degree = [0] * n
    for u, v in edges:
        degree[u] += 1
        degree[v] += 1

    # Map each non-isolated source vertex to a fresh target vertex label.
    # Isolated vertices are intentionally omitted.
    new_label = {}
    for v in range(n):
        if degree[v] > 0:
            new_label[v] = len(new_label)

    target_edges = []

    # Original edges, restricted to non-isolated vertices.
    for u, v in edges:
        target_edges.append([new_label[u], new_label[v]])

    # One gadget vertex per source edge, adjacent to both endpoints.
    gadget = len(new_label)
    for u, v in edges:
        target_edges.append([new_label[u], gadget])
        target_edges.append([new_label[v], gadget])
        gadget += 1

    return {"n": gadget, "edges": target_edges, "k": k}
