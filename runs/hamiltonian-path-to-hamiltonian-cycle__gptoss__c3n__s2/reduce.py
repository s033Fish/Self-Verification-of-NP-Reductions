"""Reduction from Hamiltonian Path to Hamiltonian Cycle.

The source problem is :class:`HamiltonianPath` (undirected graph, any
endpoints). The target problem is :class:`HamiltonianCycle` (undirected
graph, must return to the start).

For a graph ``G`` with ``n`` vertices we construct a new graph ``G'`` as
follows:

* If ``n == 0`` we output the empty graph – Hamiltonian cycles are
  impossible, matching the ``no`` answer of the source instance.
* If ``n == 1`` the source instance is trivially a ``yes`` (the single
  vertex).  Since a Hamiltonian cycle requires at least three vertices,
  we create a fixed triangle (three vertices fully connected) which is
  always a ``yes`` instance of the target problem.
* For ``n >= 2`` we add a new vertex ``s`` (label ``n``) and connect it
  to every original vertex.  The resulting graph has ``n+1`` vertices.
  It is well‑known that ``G`` has a Hamiltonian *path* iff ``G'`` has a
  Hamiltonian *cycle*: any Hamiltonian cycle in ``G'`` must use the new
  vertex exactly once, and removing it yields a Hamiltonian path in the
  original graph, and conversely a Hamiltonian path can be closed by
  connecting its two endpoints to ``s``.

The construction runs in time linear in the size of the input graph,
+hence polynomial.
"""

from __future__ import annotations

from typing import Dict, List

from problems import HamiltonianPath, HamiltonianCycle


def reduce(instance: Dict) -> Dict:
    """Reduce a Hamiltonian‑Path instance to a Hamiltonian‑Cycle instance.

    Parameters
    ----------
    instance:
        A dictionary representing an undirected graph as required by
        :class:`HamiltonianPath`.  It must contain the keys ``"n"`` and
        ``"edges"``.

    Returns
    -------
    dict
        A graph instance suitable for :class:`HamiltonianCycle` such that
        the answer to the target instance is *yes* exactly when the
        answer to the source instance is *yes*.
    """

    # Validate the source instance – will raise InvalidInstance on error.
    HamiltonianPath.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Case n == 0: empty graph – no Hamiltonian cycle.
    if n == 0:
        target = {"n": 0, "edges": []}
        HamiltonianCycle.validate(target)
        return target

    # Case n == 1: source is always yes.  Return a fixed triangle which is
    # always a yes instance for HamiltonianCycle.
    if n == 1:
        target = {"n": 3, "edges": [[0, 1], [1, 2], [2, 0]]}
        HamiltonianCycle.validate(target)
        return target

    # General case n >= 2.
    new_n = n + 1
    new_vertex = n  # label of the added vertex
    # Start with a copy of the original edges.
    new_edges: List[List[int]] = [list(e) for e in edges]
    # Connect the new vertex to every original vertex.
    for u in range(n):
        new_edges.append([u, new_vertex])

    target = {"n": new_n, "edges": new_edges}
    HamiltonianCycle.validate(target)
    return target

