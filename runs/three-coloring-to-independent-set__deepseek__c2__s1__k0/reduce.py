"""Polynomial-time reduction from 3-Coloring to Independent Set.

Construction
------------
For every vertex v of the source graph and every colour c in {0, 1, 2},
create a target vertex (v, c), encoded as the integer 3*v + c.

Target edges:
  * For every source vertex v, add the triangle
        (v,0)-(v,1), (v,0)-(v,2), (v,1)-(v,2).
    An independent set can contain at most one node per vertex, so it
    chooses at most one colour for each source vertex.
  * For every source edge {u,v} and every colour c, add
        (u,c)-(v,c).
    This forbids choosing the same colour for both endpoints of an edge.

Then the source graph is 3-colourable iff the target graph has an
independent set of size n (choose, for each vertex, the node of its
colour in a proper 3-colouring; conversely an independent set of size n
must pick exactly one node per vertex, and the cross edges make that a
proper colouring).

Set k = n.  The reduction uses O(n + m) vertices and edges, hence runs in
polynomial time.  No solver is called.
"""


def reduce(instance):
    """Map a 3-Coloring instance to an Independent Set instance."""
    n = instance["n"]
    edges = instance["edges"]

    # One target vertex per (source vertex, colour) pair.
    target_n = 3 * n
    target_edges = []

    # At most one colour per source vertex: a triangle on its three nodes.
    for v in range(n):
        base = 3 * v
        target_edges.append([base, base + 1])
        target_edges.append([base, base + 2])
        target_edges.append([base + 1, base + 2])

    # Adjacent source vertices must get different colours.
    for u, v in edges:
        bu = 3 * u
        bv = 3 * v
        target_edges.append([bu, bv])
        target_edges.append([bu + 1, bv + 1])
        target_edges.append([bu + 2, bv + 2])

    # A 3-colouring of all n vertices corresponds to an independent set
    # of exactly n target vertices.
    return {"n": target_n, "edges": target_edges, "k": n}
