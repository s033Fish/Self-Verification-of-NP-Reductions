"""Reduction from Hamiltonian Path to Hamiltonian Cycle.

Given an undirected graph G = (V, E) as an instance of Hamiltonian Path,
construct a graph G' = (V', E') as an instance of Hamiltonian Cycle such that
G has a Hamiltonian path iff G' has a Hamiltonian cycle.

The construction:
- If |V| = 1, output a fixed triangle (3-cycle), which is a yes-instance of
  Hamiltonian Cycle. The original instance is always a yes-instance.
- Otherwise, add a new vertex `new = n` and connect it to every original
  vertex. Formally, V' = V ∪ {new} and E' = E ∪ {{new, v} : v ∈ V}.

This transformation runs in polynomial time.
"""

def reduce(instance):
    """Transform a Hamiltonian Path instance into a Hamiltonian Cycle instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys "n" (int) and "edges" (list of [u, v]).

    Returns
    -------
    dict
        An instance of the Hamiltonian Cycle problem.
    """
    n = instance.get("n", 0)
    edges = instance.get("edges", [])
    # Special case: single vertex graphs are always yes for Hamiltonian Path.
    # The generic construction would produce a 2-vertex graph, which is a no-instance
    # for Hamiltonian Cycle. Instead, return a known yes-instance (a triangle).
    if n == 1:
        return {"n": 3, "edges": [[0, 1], [1, 2], [2, 0]]}
    # General construction: add a new universal vertex.
    new_n = n + 1
    new_edges = list(edges)  # copy original edges
    # Connect the new vertex (index n) to every original vertex.
    for v in range(n):
        new_edges.append([new_n - 1, v])
    return {"n": new_n, "edges": new_edges}

# The module exposes only the reduce function as required.
__all__ = ["reduce"]

