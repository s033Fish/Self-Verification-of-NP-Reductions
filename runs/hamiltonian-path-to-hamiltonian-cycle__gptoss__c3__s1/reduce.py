"""Reduction from Hamiltonian Path to Hamiltonian Cycle.

The source problem is :class:`HamiltonianPath` (undirected graph, any
endpoints). The target problem is :class:`HamiltonianCycle` (undirected
graph, must form a cycle).

For a graph ``G = (V, E)`` with ``|V| = n`` we construct a new graph
``G' = (V ∪ {v*}, E ∪ {{v*, u} : u ∈ V})`` – i.e. we add a fresh
vertex ``v*`` and connect it to every original vertex.  It is classic that
``G`` has a Hamiltonian *path* iff ``G'`` has a Hamiltonian *cycle*.

The construction works for all ``n`` except the trivial case ``n = 1``.
When ``n = 1`` the source instance is always a *yes* instance, but the
construction would yield a graph with two vertices and a single edge,
which can never contain a Hamiltonian cycle (the target would be *no*).
We therefore handle ``n = 1`` specially by returning a fixed triangle –
the smallest graph that does contain a Hamiltonian cycle.

The function runs in linear time in the size of the input instance and
produces a valid target instance according to the specifications in
``problems.py``.
"""

from __future__ import annotations

from typing import Dict, List

def reduce(instance: Dict[str, object]) -> Dict[str, object]:
    """Reduce a Hamiltonian Path instance to a Hamiltonian Cycle instance.

    Parameters
    ----------
    instance:
        A dict with keys ``"n"`` (int) and ``"edges"`` (list of [u, v]).

    Returns
    -------
    dict
        A new instance for the Hamiltonian Cycle problem such that the
        answer is *yes* exactly when the original instance is *yes*.
    """

    n: int = instance["n"]  # type: ignore[index]
    edges: List[List[int]] = list(instance["edges"])  # copy to avoid mutating input

    # Special case n == 1: the source is always yes, but the generic
    # construction would give a graph with two vertices which cannot have
    # a Hamiltonian cycle.  Return a simple triangle which is a yes-instance.
    if n == 1:
        return {"n": 3, "edges": [[0, 1], [1, 2], [2, 0]]}

    # General construction: add a new vertex indexed ``n`` and connect it
    # to every original vertex.
    new_n = n + 1
    new_edges = edges.copy()
    for v in range(n):
        new_edges.append([v, n])

    return {"n": new_n, "edges": new_edges}

