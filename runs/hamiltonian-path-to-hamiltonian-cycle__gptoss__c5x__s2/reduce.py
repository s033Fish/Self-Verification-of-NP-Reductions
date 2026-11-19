"""Reduction from Hamiltonian Path to Hamiltonian Cycle.

The source problem is :class:`HamiltonianPath` (undirected graph, any
endpoints).  The target problem is :class:`HamiltonianCycle` (undirected
graph, must return to the start).

The classic reduction adds a new universal vertex that is adjacent to
every original vertex.  A Hamiltonian cycle in the new graph must use the
new vertex exactly once, connecting two original vertices.  Removing the
new vertex yields a Hamiltonian path in the original graph, and vice‑versa.

Edge‑case handling:
* ``n == 0`` – the source instance is a definite *no*.  We return the
  same empty graph (``n == 0``) which is also a *no* for Hamiltonian Cycle.
* ``n == 1`` – a single vertex trivially has a Hamiltonian path, but the
  universal‑vertex construction would produce a graph with ``n == 2``
  which can never contain a Hamiltonian cycle.  Instead we map this case
  to a triangle (three vertices fully connected) which *does* have a
  Hamiltonian cycle.
* ``n >= 2`` – the standard construction works.

The function runs in time linear in the size of the input graph, i.e.
polynomial time.
"""

from __future__ import annotations

from typing import Dict, List

from problems import HamiltonianPath, HamiltonianCycle


def reduce(instance: Dict) -> Dict:
    """Reduce a Hamiltonian‑Path instance to a Hamiltonian‑Cycle instance.

    Parameters
    ----------
    instance:
        A dictionary representing a Hamiltonian‑Path instance.  It is
        validated using :meth:`HamiltonianPath.validate`.

    Returns
    -------
    dict
        A dictionary representing a Hamiltonian‑Cycle instance such that
        the answer to the returned instance is *yes* iff the answer to
        the input instance is *yes*.
    """
    # Validate the source instance – this will raise InvalidInstance if
    # the format is wrong.
    HamiltonianPath.validate(instance)

    n: int = instance["n"]  # type: ignore[index]
    edges: List[List[int]] = instance["edges"]  # type: ignore[index]

    # Case n == 0: trivially no for both problems.
    if n == 0:
        return {"n": 0, "edges": []}

    # Case n == 1: source is yes, we need a target that is also yes.
    # The smallest graph with a Hamiltonian cycle is a triangle.
    if n == 1:
        # Vertices 0,1,2 form a triangle.
        triangle_edges = [[0, 1], [1, 2], [2, 0]]
        return {"n": 3, "edges": triangle_edges}

    # General case n >= 2.
    new_n = n + 1
    new_vertex = n  # index of the added universal vertex
    # Copy original edges (they are already validated as undirected and
    # without duplicates).
    new_edges = [list(e) for e in edges]
    # Connect the new vertex to every original vertex.
    for v in range(n):
        new_edges.append([new_vertex, v])

    # Validate the produced instance for the target problem.
    target_instance = {"n": new_n, "edges": new_edges}
    HamiltonianCycle.validate(target_instance)
    return target_instance

