"""Polynomial-time reduction from Hamiltonian Path to Hamiltonian Cycle.

Source (Hamiltonian Path, undirected, any endpoints):
    {"n": n, "edges": [[u, v], ...]}
    Vertices 0..n-1, undirected simple edges.

Target (Hamiltonian Cycle, undirected):
    {"n": n, "edges": [[u, v], ...]}
    Vertices 0..n-1, undirected simple edges.

Reduction
---------
For a source graph G with n >= 2 vertices, add one new vertex x = n and
connect it to every vertex of G.  The resulting graph G' has n + 1
vertices.

* If G has a Hamiltonian path v_1, ..., v_n, then
  x - v_1 - ... - v_n - x is a Hamiltonian cycle in G'.
* If G' has a Hamiltonian cycle, then x has exactly two neighbours in
  that cycle; deleting x leaves a Hamiltonian path in G through all n
  original vertices.

Hence for n >= 2, G has a Hamiltonian path iff G' has a Hamiltonian
cycle.  (This also correctly handles n = 2: G' is a triangle exactly
when the edge [0, 1] is present.)

Edge cases
----------
* n = 0: the source is no.  The construction yields a 1-vertex graph,
  which has no cycle, so the target is no as well.
* n = 1: the source is yes (the single vertex is a path), but the
  construction would yield only 2 vertices, which can never have a
  cycle.  We therefore map this case directly to a yes-instance of
  Hamiltonian Cycle: the triangle on 3 vertices.

The reduction only adds n edges and one vertex, so it runs in
polynomial time and never calls a solver.
"""


def reduce(instance):
    """Map a Hamiltonian Path instance to a Hamiltonian Cycle instance."""
    n = instance["n"]
    edges = instance["edges"]

    # n = 1 is yes for Hamiltonian Path, but the gadget would create a
    # 2-vertex graph, which is always no for Hamiltonian Cycle.  Map it
    # to the smallest yes-instance of the target (the triangle).
    if n == 1:
        return {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}

    new_vertex = n
    new_edges = [[u, v] for (u, v) in edges]
    for v in range(n):
        new_edges.append([v, new_vertex])

    return {"n": n + 1, "edges": new_edges}
