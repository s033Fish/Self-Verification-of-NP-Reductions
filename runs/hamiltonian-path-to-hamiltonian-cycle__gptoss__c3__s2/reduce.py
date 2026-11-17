"""Reduction from Hamiltonian Path (undirected) to Hamiltonian Cycle (undirected).

The source problem instance is a dictionary with keys "n" and "edges" as
described in ``problems.HamiltonianPath``.  The target problem expects the same
format but interpreted as a Hamiltonian Cycle instance.

We implement the classic polynomial‑time reduction:

* For a graph G = (V, E) with |V| >= 2 we add a new vertex ``x`` and connect
  it to every vertex of V.  G has a Hamiltonian path iff the new graph G' has a
  Hamiltonian cycle (the cycle must contain ``x`` and the two neighbours of ``x``
  correspond to the endpoints of the path).

* Small edge‑cases need special handling because the target problem declares
  that graphs with ``n <= 2`` are always *no*.

  - ``n = 0``: the source answer is *no*.  We return the empty graph (still no).
  - ``n = 1``: the source answer is *yes* (the single vertex is a trivial path).
    To obtain a *yes* instance for Hamiltonian Cycle we construct a triangle on
    three vertices – a guaranteed Hamiltonian cycle.
  - ``n = 2``: the generic construction works.  Adding a new vertex connected to
    both original vertices yields a triangle exactly when the original edge is
    present, matching the source answer.

The implementation validates the input using the source class and returns a
valid target instance.  All operations are clearly polynomial in the size of
the input.
"""

from __future__ import annotations

from typing import List, Dict, Any

# Import the problem classes to reuse validation helpers.
from problems import HamiltonianPath, HamiltonianCycle


def _add_edge(edge_set: set[frozenset[int]], u: int, v: int) -> None:
    """Add an undirected edge to ``edge_set`` represented as a frozenset.

    The helper is only used internally to avoid duplicate edges.
    """
    edge_set.add(frozenset((u, v)))


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Hamiltonian‑Path instance to a Hamiltonian‑Cycle instance.

    Parameters
    ----------
    instance:
        A valid ``HamiltonianPath`` instance (validated by the caller).

    Returns
    -------
    dict
        A valid ``HamiltonianCycle`` instance such that the answer to the
        target instance is *yes* exactly when the answer to the source instance
        is *yes*.
    """
    # Ensure the input follows the source specification.
    HamiltonianPath.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Edge set for quick duplicate detection when we build the new graph.
    edge_set: set[frozenset[int]] = set()
    for u, v in edges:
        edge_set.add(frozenset((u, v)))

    # ------------------------------------------------------------------
    # Handle the small‑graph edge cases explicitly.
    # ------------------------------------------------------------------
    if n == 0:
        # Source is always NO; returning any graph with n <= 2 keeps it NO.
        return {"n": 0, "edges": []}

    if n == 1:
        # Source is YES.  Construct a triangle (3‑cycle) which is a YES for HC.
        # Vertices: 0 (original), 1, 2.
        triangle_edges = [[0, 1], [1, 2], [2, 0]]
        return {"n": 3, "edges": triangle_edges}

    # ------------------------------------------------------------------
    # General case n >= 2.
    # ------------------------------------------------------------------
    new_n = n + 1
    new_vertex = n  # the added vertex index.

    # Start with the original edges.
    new_edges: List[List[int]] = [list(edge) for edge in edges]

    # Connect the new vertex to every original vertex.
    for v in range(n):
        # Avoid adding duplicate edges (shouldn't happen, but we stay safe).
        if frozenset((new_vertex, v)) not in edge_set:
            new_edges.append([new_vertex, v])
            edge_set.add(frozenset((new_vertex, v)))

    # Validate the constructed target instance before returning.
    target_instance = {"n": new_n, "edges": new_edges}
    HamiltonianCycle.validate(target_instance)
    return target_instance

