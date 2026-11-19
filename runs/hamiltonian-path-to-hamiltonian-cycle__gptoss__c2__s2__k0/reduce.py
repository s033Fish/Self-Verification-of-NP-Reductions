"""Reduction from Hamiltonian Path to Hamiltonian Cycle.

Given an undirected graph G = (V, E) with |V| = n, we construct a new graph G'
by adding a new vertex s (indexed n) and connecting it to every vertex of G.
For n >= 2 this transformation satisfies:
    G has a Hamiltonian path ⇔ G' has a Hamiltonian cycle.
For the small edge cases we handle them explicitly:
  * n = 0 (no vertices): source answer is NO. We output an empty graph
    (n' = 0) which is also a NO-instance for Hamiltonian Cycle.
  * n = 1 (single vertex): source answer is YES. We output a triangle
    (3 vertices, all edges) which is a YES-instance for Hamiltonian Cycle.
  * n = 2: the general construction works (produces a 3‑vertex graph).
"""

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Transform a Hamiltonian Path instance into a Hamiltonian Cycle instance.

    Parameters
    ----------
    instance: dict with keys "n" and "edges" as defined for HamiltonianPath.

    Returns
    -------
    dict with keys "n" and "edges" for HamiltonianCycle.
    """
    n: int = instance["n"]
    edges: List[List[int]] = instance.get("edges", [])

    # Edge case n = 0: output a trivial no-instance (empty graph)
    if n == 0:
        return {"n": 0, "edges": []}

    # Edge case n = 1: source is always YES. Return a triangle (always YES for cycle).
    if n == 1:
        return {"n": 3, "edges": [[0, 1], [1, 2], [2, 0]]}

    # General case: add a new vertex indexed n and connect it to all existing vertices.
    new_n = n + 1
    # Copy original edges (they are undirected, stored as [u, v] with u != v)
    new_edges = [list(e) for e in edges]
    # Add edges from the new vertex to each old vertex.
    for i in range(n):
        new_edges.append([n, i])

    return {"n": new_n, "edges": new_edges}


if __name__ == "__main__":
    # Simple manual test when run directly (not used in the evaluation).
    import json, sys
    data = json.load(sys.stdin)
    json.dump(reduce(data), sys.stdout)
