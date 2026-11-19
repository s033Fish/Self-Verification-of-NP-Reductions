"""Reduction from Hamiltonian Path to Hamiltonian Cycle.

Given an undirected graph G = (V, E) for the Hamiltonian Path problem,
construct a graph G' = (V', E') for the Hamiltonian Cycle problem such that
G has a Hamiltonian path iff G' has a Hamiltonian cycle.

Construction:
- If |V| = 0: output an empty graph (n=0). Both instances are NO.
- If |V| = 1: output a triangle (3 vertices, all three edges). The source
  instance is YES, and the triangle has a Hamiltonian cycle, so the target
  instance is YES.
- Otherwise (n >= 2): add a new vertex s connected to every original vertex.
  Let V' = V ∪ {s}. Then G has a Hamiltonian path iff G' has a Hamiltonian cycle.
"""

def reduce(instance):
    n = instance.get("n")
    original_edges = instance.get("edges", [])
    # store edges as unordered pairs (min, max) in a set to avoid duplicates
    edge_set = set()
    for u, v in original_edges:
        a, b = (u, v) if u < v else (v, u)
        edge_set.add((a, b))

    # Edge cases
    if n == 0:
        # Empty graph; Hamiltonian cycle is impossible (n <= 2)
        return {"n": 0, "edges": []}
    if n == 1:
        # Single vertex graph has a Hamiltonian path.
        # Return a triangle which always has a Hamiltonian cycle.
        return {"n": 3, "edges": [[0, 1], [0, 2], [1, 2]]}

    # General case: n >= 2
    new_n = n + 1
    s = n  # index of the new vertex
    # Add edges from the new vertex to every original vertex
    for v in range(n):
        a, b = (v, s) if v < s else (s, v)
        edge_set.add((a, b))

    # Convert edge set back to list of [u, v]
    new_edges = [list(e) for e in edge_set]
    return {"n": new_n, "edges": new_edges}

# The module only needs to expose the reduce function.
__all__ = ["reduce"]
