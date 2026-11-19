"""Polynomial-time reduction from Hamiltonian Path to Hamiltonian Cycle.

Given an undirected graph G on n vertices, the standard reduction adds one
new vertex x adjacent to every original vertex.  A Hamiltonian path
v1, ..., vn in G becomes the Hamiltonian cycle x, v1, ..., vn, x in G+x,
and conversely any Hamiltonian cycle in G+x uses exactly two edges incident
to x, so deleting x leaves a Hamiltonian path in G.

The only exception is n = 1: the source is always yes, but the target graph
would have only 2 vertices and therefore can never contain a cycle.  In that
case we map to a triangle.  For n = 0 the source is no, so we map to an
edgeless graph on 0 vertices (also no).
"""


def reduce(instance):
    """Return a Hamiltonian Cycle instance equivalent to the given
    Hamiltonian Path instance.

    Both instances use the format {"n": n, "edges": [[u, v], ...]}.
    """
    n = instance["n"]
    edges = instance["edges"]

    # n = 0: source is no.  The empty graph on 0 vertices is also no.
    if n == 0:
        return {"n": 0, "edges": []}

    # n = 1: source is always yes.  The target needs at least 3 vertices,
    # so use a triangle, which is yes.
    if n == 1:
        return {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}

    # n >= 2: add a new universal vertex numbered n, joined to every
    # original vertex.  The original edges are copied unchanged.
    new_edges = [list(edge) for edge in edges]
    for v in range(n):
        new_edges.append([v, n])

    return {"n": n + 1, "edges": new_edges}
