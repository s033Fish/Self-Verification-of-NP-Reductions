"""Polynomial-time reduction from Hamiltonian Path to Hamiltonian Cycle.

Construction
------------
Given an undirected graph G on vertices 0..n-1, build G' by adding one new
vertex x = n and joining it to every vertex of G.

* If G has a Hamiltonian path v1 - v2 - ... - vn, then
  x - v1 - v2 - ... - vn - x is a Hamiltonian cycle of G' (x is adjacent to
  every vertex, in particular to v1 and vn).

* If G' has a Hamiltonian cycle, it visits x; deleting x from that cycle
  leaves a path through all n original vertices, i.e. a Hamiltonian path of G.

Hence for n >= 2 the two answers coincide.

Degenerate cases:
* n = 0: G has no Hamiltonian path, and G' would have a single vertex with no
  cycle.  We return an empty graph, which is a "no" instance of the target.
* n = 1: G has a Hamiltonian path (the lone vertex), but the construction above
  would give a 2-vertex graph with no cycle.  We instead return the triangle,
  a "yes" instance of the target.

The construction runs in O(n + |E|) time and produces a valid target instance.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]

    if n == 0:
        # Source is "no"; return a valid "no" target instance.
        return {"n": 0, "edges": []}

    if n == 1:
        # Source is "yes" (single vertex path); the triangle is a "yes" target.
        return {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}

    new_vertex = n
    new_edges = [list(edge) for edge in edges]
    for v in range(n):
        new_edges.append([v, new_vertex])
    return {"n": n + 1, "edges": new_edges}
