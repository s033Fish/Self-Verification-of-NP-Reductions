"""Polynomial-time reduction from 3-Coloring to Independent Set.

Given a 3-Coloring instance with n vertices, create three vertices per
original vertex, one for each possible colour.  The three copies of each
original vertex form a triangle, so an independent set can contain at most
one copy per original vertex.  For every original edge {u, v}, connect
every copy of u to every copy of v, so the chosen copies of adjacent
original vertices must have different colours.

The original graph is 3-colourable iff the constructed graph has an
independent set of size at least n.
"""


def reduce(instance):
    """Reduce a 3-Coloring instance to an Independent Set instance."""
    n = instance["n"]
    edges = instance["edges"]

    new_edges = []

    # Triangle for each original vertex: at most one colour can be chosen.
    for v in range(n):
        base = 3 * v
        new_edges.append([base, base + 1])
        new_edges.append([base, base + 2])
        new_edges.append([base + 1, base + 2])

    # For each original edge, forbid equal colours at its endpoints.
    for u, v in edges:
        base_u = 3 * u
        base_v = 3 * v
        for cu in range(3):
            for cv in range(3):
                new_edges.append([base_u + cu, base_v + cv])

    return {"n": 3 * n, "edges": new_edges, "k": n}
