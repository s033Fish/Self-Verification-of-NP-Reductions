"""Polynomial-time reduction from 3-Coloring to Independent Set.

Given a 3-Coloring instance G = (V, E) with |V| = n, build an
Independent Set instance H as follows.

For every vertex v in V and every colour c in {0, 1, 2}, create a
vertex (v, c) of H.  So H has 3n vertices.

Edges of H:
  * For each v in V, add the triangle (v,0)-(v,1), (v,0)-(v,2),
    (v,1)-(v,2).  An independent set may therefore contain at most one
    colour copy of each original vertex.
  * For each edge {u, v} in E and each colour c in {0, 1, 2}, add the
    edge (u,c)-(v,c).  An independent set may therefore not pick the
    same colour for two adjacent original vertices.

Set k = n.  An independent set of size n in H picks exactly one colour
copy for every original vertex (one per triangle), and the second family
of edges guarantees adjacent vertices receive different colours.  Hence
H has an independent set of size >= n iff G is 3-colourable.

The construction uses 3n vertices and 3n + 3|E| edges, so it runs in
polynomial time (linear in the size of the input).
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    # Map original vertex v, colour c to its vertex id in H.
    def vid(v, c):
        return 3 * v + c

    new_n = 3 * n
    new_edges = []

    # At most one colour per original vertex.
    for v in range(n):
        new_edges.append([vid(v, 0), vid(v, 1)])
        new_edges.append([vid(v, 0), vid(v, 2)])
        new_edges.append([vid(v, 1), vid(v, 2)])

    # Adjacent original vertices must not share a colour.
    for u, v in edges:
        for c in range(3):
            new_edges.append([vid(u, c), vid(v, c)])

    return {"n": new_n, "edges": new_edges, "k": n}
