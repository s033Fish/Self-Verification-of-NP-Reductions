"""Polynomial-time reduction from 3-Coloring to Independent Set.

Construction (standard "gadget" reduction):
  * For every vertex v of the source graph and every colour c in {0,1,2},
    create a target vertex (v, c), indexed as v*3 + c.
  * For every source vertex v, add edges between (v, c) and (v, c')
    for c != c', so an independent set can pick at most one colour per
    source vertex.
  * For every source edge {u, v} and every colour c, add an edge between
    (u, c) and (v, c), so adjacent source vertices cannot receive the
    same colour.

The source graph is 3-colourable iff the target graph has an independent
set of size n (one colour choice per source vertex).  Hence we set k = n.

Edge cases:
  * n = 0 -> target n = 0, k = 0, which is yes (k <= 0).
  * k = n <= 3 -> always yes, matching "any graph with <= 3 vertices is yes".
  * K4 -> no independent set of size 4, matching "K4 is no".
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    # Target graph has 3 nodes per source vertex.
    new_n = 3 * n
    new_edges = []

    def node(v, c):
        return 3 * v + c

    # At most one colour per source vertex.
    for v in range(n):
        for c1 in range(3):
            for c2 in range(c1 + 1, 3):
                new_edges.append([node(v, c1), node(v, c2)])

    # Adjacent source vertices must get different colours.
    for u, v in edges:
        for c in range(3):
            new_edges.append([node(u, c), node(v, c)])

    return {"n": new_n, "edges": new_edges, "k": n}
