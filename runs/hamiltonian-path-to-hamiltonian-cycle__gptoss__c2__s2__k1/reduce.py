"""Reduction from Hamiltonian Path to Hamiltonian Cycle.

Given an undirected graph G = (V, E) with vertices 0..n-1, we construct a
graph G' for the Hamiltonian Cycle problem.

For n >= 2 we add a new vertex v = n and connect it to every original
vertex.  Then G has a Hamiltonian path iff G' has a Hamiltonian cycle:
* If G has a Hamiltonian path v1-...-vn, then v - v1-...-vn - v is a Hamiltonian
  cycle in G'.
* Conversely, any Hamiltonian cycle in G' must include v with exactly two
  neighbours a and b; removing v yields a Hamiltonian path a-...-b in G.

Edge cases:
- n = 0: source instance is a "no".  G' will have a single vertex (n'=1) and
  by the target definition n <= 2 is always "no".
- n = 1: source instance is a "yes" (the single vertex is a trivial path),
  but the above construction would give n'=2 which is always "no" for the
  target.  We therefore output a fixed triangle (3 vertices, all edges),
  which is a "yes" instance for Hamiltonian Cycle.
- n = 2: the generic construction works correctly, matching the source
  condition that the edge [0,1] must exist.
"""

def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    # Ensure edges are a list of [u, v]
    # For n >= 2, add a new vertex n and connect it to all existing vertices.
    if n == 0:
        # Return a graph with 0 vertices (or 1 vertex) which is a "no" for Hamiltonian Cycle.
        return {"n": 0, "edges": []}
    if n == 1:
        # Return a triangle which has a Hamiltonian cycle.
        # Use vertices 0,1,2.
        return {"n": 3, "edges": [[0,1],[1,2],[2,0]]}
    # n >= 2 case
    new_n = n + 1
    new_edges = list(edges)  # copy original edges
    # Add edges between new vertex (index n) and each original vertex i.
    for i in range(n):
        new_edges.append([n, i])
    return {"n": new_n, "edges": new_edges}

# The module exposes only the reduce function as required.
