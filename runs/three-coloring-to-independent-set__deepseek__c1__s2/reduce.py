"""Polynomial-time reduction from 3-Coloring to Independent Set.

Construction (standard):
For a 3-Coloring instance G = (V, E) with |V| = n, build a graph H whose
vertices are pairs (v, c) for v in V and c in {0, 1, 2}; i.e. 3n vertices
indexed as 3*v + c.

Edges of H:
  * For every v in V, add the triangle {(v,0), (v,1), (v,2)} so that at
    most one colour can be chosen for each vertex.
  * For every edge {u, v} in E and every colour c, add {(u,c), (v,c)} so
    that adjacent vertices cannot share a colour.

Set k = n.  A proper 3-colouring of G yields an independent set of size n
(one vertex (v, colour(v)) per v), and conversely any independent set of
size n in H must contain exactly one (v,c) per v (because of the vertex
triangles) with no colour conflicts (because of the edge gadgets), which
gives a proper 3-colouring.  Hence H has an independent set of size >= n
iff G is 3-colourable.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    new_edges = []

    # One triangle per original vertex: at most one colour per vertex.
    for v in range(n):
        a = 3 * v
        new_edges.append([a, a + 1])
        new_edges.append([a + 1, a + 2])
        new_edges.append([a, a + 2])

    # For each original edge, forbid the same colour at both endpoints.
    for u, v in edges:
        for c in range(3):
            new_edges.append([3 * u + c, 3 * v + c])

    return {"n": 3 * n, "edges": new_edges, "k": n}
