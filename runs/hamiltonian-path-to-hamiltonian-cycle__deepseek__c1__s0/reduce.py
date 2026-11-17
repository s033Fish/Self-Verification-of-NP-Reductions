"""Polynomial-time reduction from Hamiltonian Path to Hamiltonian Cycle.

Construction
------------
Given an undirected graph G on vertices 0..n-1, add one new universal
vertex x = n joined to every original vertex.  Any Hamiltonian path
v_1, ..., v_n of G becomes the Hamiltonian cycle
x, v_1, ..., v_n, x in the new graph.  Conversely, any Hamiltonian cycle
of the new graph uses exactly two edges incident to x, and deleting x
from that cycle leaves a Hamiltonian path of G.

This is correct for n >= 2 (and for n = 0, where both answers are no).
The single-vertex case n = 1 is special: the source is yes, but adding a
universal vertex yields only two vertices, which cannot contain a cycle.
We therefore map n = 1 to the triangle, which is a yes-instance of
Hamiltonian Cycle.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    if n == 1:
        # The unique one-vertex graph has a Hamiltonian path, so the
        # target must be a yes-instance.  The triangle is the smallest
        # graph with a Hamiltonian cycle.
        return {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}

    # Add a new vertex n connected to all original vertices.
    new_edges = [list(edge) for edge in edges]
    new_edges.extend([[v, n] for v in range(n)])
    return {"n": n + 1, "edges": new_edges}
