"""Polynomial-time reduction from 3-Coloring to Independent Set.

Given a graph G with n vertices, build a graph H as follows:

  * For every vertex v of G and every colour c in {0, 1, 2}, create a
    vertex (v, c) of H.  So H has 3n vertices.
  * For every vertex v of G, add the three edges of the triangle
    {(v,0), (v,1), (v,2)}.  This forces an independent set to pick at
    most one colour per original vertex.
  * For every edge {u, v} of G and every colour c, add the edge
    {(u,c), (v,c)}.  This forbids adjacent original vertices from
    receiving the same colour.

Set k = n.  Then H has an independent set of size at least n iff G has a
proper 3-colouring:

  * A proper 3-colouring of G yields the independent set
    {(v, colour(v)) : v in V(G)}, which has exactly n vertices and no
    edges between any two of them.
  * An independent set of size n in H must contain exactly one vertex
    (v, c_v) for each original vertex v (triangles limit it to at most
    one, and there are only 3n vertices but n groups).  The conflict
    edges guarantee c_u != c_v for every edge {u, v} of G, so the map
    v -> c_v is a proper 3-colouring.

The construction is clearly polynomial in the size of the input.
"""


def reduce(instance):
    """Reduce a 3-Coloring instance to an Independent Set instance."""
    n = instance["n"]
    edges = instance["edges"]

    # New vertices: (v, c) is encoded as 3*v + c.
    new_edges = []

    # Triangle for each original vertex: at most one colour per vertex.
    for v in range(n):
        new_edges.append([3 * v + 0, 3 * v + 1])
        new_edges.append([3 * v + 1, 3 * v + 2])
        new_edges.append([3 * v + 0, 3 * v + 2])

    # Conflict edges: adjacent vertices may not share a colour.
    for u, v in edges:
        for c in range(3):
            new_edges.append([3 * u + c, 3 * v + c])

    return {"n": 3 * n, "edges": new_edges, "k": n}
