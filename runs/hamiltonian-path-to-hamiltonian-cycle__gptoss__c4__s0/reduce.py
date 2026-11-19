"""Reduction from Hamiltonian Path to Hamiltonian Cycle.

The reduction is deterministic and runs in polynomial time.

Given an undirected graph G = (V, E) with |V| = n, we construct a new
graph G' = (V', E') where:

* If n == 0 we output the empty graph (n' = 0).  The target instance is a
  definite NO because Hamiltonian cycles require at least three vertices.

* If n == 1 the source instance is trivially a YES (the single vertex is a
  Hamiltonian path).  To preserve the answer we output a triangle on three
  vertices, which always has a Hamiltonian cycle.

* For n >= 2 we add a fresh vertex s and connect it to every vertex of the
  original graph.  Formally, V' = V ∪ {s} and E' = E ∪ {{v, s} : v ∈ V}.
  It is well‑known that G has a Hamiltonian path iff G' has a Hamiltonian
  cycle: a Hamiltonian path in G can be closed into a cycle by using the two
  edges incident to s, and any Hamiltonian cycle in G' must use s exactly once,
  thereby splitting the cycle into a Hamiltonian path of G.

The implementation below follows this description and also validates the
input using the problem class provided in ``problems.py``.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import HamiltonianPath, HamiltonianCycle


def _validate_source(instance: Dict[str, Any]) -> None:
    """Validate the source instance using the provided class method.

    ``HamiltonianPath.validate`` raises ``InvalidInstance`` on malformed input.
    We simply forward the call – any exception will propagate, which is the
    expected behaviour for an invalid reduction input.
    """

    HamiltonianPath.validate(instance)


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Hamiltonian‑Path instance to a Hamiltonian‑Cycle instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` and ``"edges"`` representing an
        undirected graph as described in the ``HamiltonianPath`` docstring.

    Returns
    -------
    dict
        An instance of the target problem (Hamiltonian Cycle) that is a YES
        exactly when the input instance is a YES.
    """

    _validate_source(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Edge‑case handling
    if n == 0:
        # Empty graph – always NO for Hamiltonian cycle.
        return {"n": 0, "edges": []}

    if n == 1:
        # Source is YES.  Return a triangle (3‑vertex complete graph) which is
        # guaranteed to have a Hamiltonian cycle.
        return {"n": 3, "edges": [[0, 1], [1, 2], [2, 0]]}

    # General case n >= 2
    new_vertex = n
    # Start with a shallow copy of the original edge list.
    new_edges: List[List[int]] = [edge[:] for edge in edges]
    # Connect the new vertex to every existing vertex.
    for v in range(n):
        new_edges.append([v, new_vertex])

    return {"n": n + 1, "edges": new_edges}

