"""Reduction from Hamiltonian Path to Hamiltonian Cycle.

The source problem (HamiltonianPath) asks whether an undirected graph
contains a Hamiltonian *path* (a simple path visiting every vertex exactly
once).  The target problem (HamiltonianCycle) asks whether an undirected
graph contains a Hamiltonian *cycle* (a simple cycle visiting every vertex
exactly once and returning to the start).

Standard reduction:
    Given a graph G = (V, E) with |V| = n, create a new graph G' by adding a
    fresh vertex v_new and connecting it to every vertex of G.  Formally:
        V' = V ∪ {v_new}
        E' = E ∪ { {v, v_new} : v ∈ V }
    Any Hamiltonian cycle in G' must include v_new; removing v_new yields a
    Hamiltonian path in G.  Conversely, any Hamiltonian path in G can be
    turned into a Hamiltonian cycle in G' by adding the two edges from
    v_new to the endpoints of the path (which always exist because v_new is
    universal).  Hence G has a Hamiltonian path iff G' has a Hamiltonian
    cycle.

Edge‑case handling:
* n = 0 – the source instance is a “no”.  The construction yields a graph
  with a single vertex, which has no Hamiltonian cycle (the target also
  answers “no”).
* n = 1 – the source instance is always “yes”.  Adding a universal vertex
  would give a 2‑vertex graph, which can never have a Hamiltonian cycle.
  To preserve correctness we special‑case this and output a triangle
  (3‑vertex complete graph), which trivially has a Hamiltonian cycle.
* n = 2 – the generic construction works: the resulting 3‑vertex graph has a
  Hamiltonian cycle exactly when the original edge (0,1) exists, matching
  the source condition.

The function runs in O(n + m) time, which is polynomial.
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a HamiltonianPath instance to a HamiltonianCycle instance.

    Parameters
    ----------
    instance: dict
        {"n": int, "edges": [[u, v], ...]} describing an undirected
        graph for the Hamiltonian Path problem.

    Returns
    -------
    dict
        An instance of the Hamiltonian Cycle problem with the same format.
    """
    n: int = instance["n"]
    edges: List[List[int]] = instance.get("edges", [])

    # Special case for n == 1: produce a triangle which always has a
    # Hamiltonian cycle.
    if n == 1:
        return {"n": 3, "edges": [[0, 1], [1, 2], [2, 0]]}

    # General case: add a new vertex indexed by n and connect it to every
    # existing vertex.
    new_n = n + 1
    # Copy existing edges to avoid mutating the input.
    new_edges: List[List[int]] = [list(e) for e in edges]
    for v in range(n):
        new_edges.append([v, n])

    return {"n": new_n, "edges": new_edges}

