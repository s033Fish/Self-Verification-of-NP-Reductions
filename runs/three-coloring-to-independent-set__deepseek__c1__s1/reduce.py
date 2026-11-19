"""Polynomial-time reduction from 3-Coloring to Independent Set.

For a source graph with n vertices, build a target graph with 3 vertices per
source vertex: vertex v becomes three vertices 3*v, 3*v+1, 3*v+2, one for each
possible colour.  The three vertices of each triple are made mutually adjacent
so an independent set can choose at most one colour for v.  For every source
edge {u, v}, add an edge between the colour-c vertices of u and v for each
colour c, so the same colour cannot be chosen for both endpoints.

The source graph is 3-colourable iff the target graph has an independent set
of size n, hence we set k = n.
"""


def reduce(instance):
    """Return an Independent Set instance equivalent to the given 3-Coloring instance."""
    n = instance["n"]
    source_edges = instance["edges"]

    target_edges = []

    # One triangle per source vertex: at most one colour may be selected.
    for v in range(n):
        a = 3 * v
        b = a + 1
        c = a + 2
        target_edges.append([a, b])
        target_edges.append([b, c])
        target_edges.append([a, c])

    # For each source edge, forbid equal colours at its two endpoints.
    for u, v in source_edges:
        for colour in range(3):
            target_edges.append([3 * u + colour, 3 * v + colour])

    return {"n": 3 * n, "edges": target_edges, "k": n}
