"""Polynomial-time reduction from Hamiltonian Path to Hamiltonian Cycle.

Given an undirected graph G on n vertices, build G' by adding one new
vertex x adjacent to every vertex of G.

Claim: G has a Hamiltonian path  <=>  G' has a Hamiltonian cycle.

  (=>) If v1 - v2 - ... - vn is a Hamiltonian path of G, then
       x - v1 - v2 - ... - vn - x is a Hamiltonian cycle of G'.

  (<=) Any Hamiltonian cycle of G' must use x (it is a vertex), and x's
       only neighbours are the original vertices.  Removing x from the
       cycle leaves a path through all n original vertices, i.e. a
       Hamiltonian path of G.

The construction needs the target graph to have at least 3 vertices, so
the degenerate source cases are handled explicitly:

  * n = 0: the source is "no"; return an empty graph (target "no").
  * n = 1: the source is "yes" (a single vertex is a path); return a
    triangle (target "yes").
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    if n == 0:
        # No Hamiltonian path exists; return a graph with no cycle.
        return {"n": 0, "edges": []}

    if n == 1:
        # Single vertex is a Hamiltonian path; return the triangle, the
        # smallest graph with a Hamiltonian cycle.
        return {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}

    # n >= 2: add a new vertex n adjacent to every original vertex.
    new_edges = [list(edge) for edge in edges]
    new_edges.extend([v, n] for v in range(n))
    return {"n": n + 1, "edges": new_edges}
