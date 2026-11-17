"""Reduction from Hamiltonian Path to Hamiltonian Cycle.

The source problem is :class:`problems.HamiltonianPath` and the target
problem is :class:`problems.HamiltonianCycle` (both defined in ``problems.py``).

For a given undirected graph G = (V, E) we construct a new graph G' = (V', E')
as follows:

* If ``n == 0`` (empty graph) the answer to the source is *no*.  We return an
  empty graph, which is also a *no* instance for Hamiltonian Cycle.
* If ``n == 1`` the source instance is trivially a *yes* (a single vertex is a
  Hamiltonian path).  The standard construction (adding a universal vertex) would
  produce a graph with two vertices, which cannot contain a Hamiltonian cycle.
  To handle this edge case we output a fixed triangle – a graph with a known
  Hamiltonian cycle – thereby preserving the answer.
* For ``n >= 2`` we add a new vertex ``s`` (indexed ``n``) and connect it to
  every original vertex.  Formally:

  ``V' = V ∪ {s}``
  ``E' = E ∪ {{s, v} | v ∈ V}``

  It is well‑known that G has a Hamiltonian *path* iff G' has a Hamiltonian
  *cycle*: the endpoints of a Hamiltonian path can be linked via ``s`` to obtain
  a cycle, and any Hamiltonian cycle in G' must contain ``s`` (since ``s`` has
  degree ``|V|``) and removing it yields a Hamiltonian path in G.

The reduction runs in O(|V| + |E|) time, i.e. polynomial.
"""

from __future__ import annotations

from typing import List, Dict, Any

import problems  # The module containing HamiltonianPath and HamiltonianCycle


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Hamiltonian‑Path instance to a Hamiltonian‑Cycle instance.

    Parameters
    ----------
    instance:
        A dictionary representing a Hamiltonian Path instance as defined in
        ``problems.HamiltonianPath``.

    Returns
    -------
    dict
        A dictionary representing a Hamiltonian Cycle instance.  The returned
        instance is *yes* exactly when the input instance is *yes*.
    """

    # Validate the source instance (may raise InvalidInstance).
    problems.HamiltonianPath.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Edge case n == 0: both problems are a definite "no".
    if n == 0:
        return {"n": 0, "edges": []}

    # Edge case n == 1: source is yes, so we must output a yes‑instance for the
    # target.  The smallest graph with a Hamiltonian cycle is a triangle.
    if n == 1:
        return {"n": 3, "edges": [[0, 1], [1, 2], [2, 0]]}

    # General case n >= 2.
    new_n = n + 1
    new_vertex = n  # index of the added universal vertex

    # Copy original edges.
    new_edges: List[List[int]] = [edge.copy() for edge in edges]

    # Connect the new vertex to every original vertex.
    for v in range(n):
        new_edges.append([new_vertex, v])

    # Return a well‑formed HamiltonianCycle instance.
    result = {"n": new_n, "edges": new_edges}
    # Validate target instance before returning (helps catch bugs early).
    problems.HamiltonianCycle.validate(result)
    return result
