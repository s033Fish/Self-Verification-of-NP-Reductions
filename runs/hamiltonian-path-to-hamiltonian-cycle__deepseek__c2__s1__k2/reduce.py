def reduce(instance):
    """Polynomial-time reduction from Hamiltonian Path to Hamiltonian Cycle.

    For n >= 2, add a new vertex n adjacent to every original vertex.
    A Hamiltonian path v0, v1, ..., v_{n-1} in the original graph becomes
    the Hamiltonian cycle n, v0, v1, ..., v_{n-1}, n in the new graph,
    and conversely every Hamiltonian cycle in the new graph must use the
    new vertex and, after removing it, gives a Hamiltonian path in the
    original graph.

    Edge cases:
      * n = 0 is no for the source; return an empty graph (also no).
      * n = 1 is yes for the source; the standard construction would give
        a 2-vertex graph, which has no cycle, so return a triangle instead.
    """
    n = instance["n"]
    edges = [list(edge) for edge in instance["edges"]]

    if n == 0:
        # No Hamiltonian path; target with no vertices has no cycle.
        return {"n": 0, "edges": []}

    if n == 1:
        # The single vertex is a Hamiltonian path; the triangle is a
        # Hamiltonian cycle.
        return {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}

    # Add universal vertex n connected to every original vertex.
    new_edges = edges + [[n, v] for v in range(n)]
    return {"n": n + 1, "edges": new_edges}
