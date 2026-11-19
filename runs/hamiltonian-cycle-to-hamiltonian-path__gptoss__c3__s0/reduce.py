"""Reduction from Hamiltonian Cycle to Hamiltonian Path.

The source problem is ``HamiltonianCycle`` (undirected).  The target problem
is ``HamiltonianPath`` (undirected, any endpoints).

We use a standard reduction that forces the Hamiltonian path to start and end
at two distinguished vertices.  The construction is as follows:

* Let the original graph have vertices ``0 .. n-1``.
* Introduce three new vertices:
    - ``v_out`` = ``n`` – a copy of vertex ``0``.
    - ``s`` = ``n+1`` – a leaf attached only to the original ``0``.
    - ``t`` = ``n+2`` – a leaf attached only to ``v_out``.
* Add the edge ``[0, v_out]``.
* For every edge ``[0, v]`` in the original graph, add edges ``[0, v]`` and
  ``[v_out, v]`` to the new graph (i.e., duplicate the adjacency of ``0`` to
  ``v_out``).
* All other edges are kept unchanged.
* Finally add the leaf edges ``[s, 0]`` and ``[v_out, t]``.

The resulting graph has ``n+3`` vertices.  Any Hamiltonian path in this graph
must start at ``s`` and end at ``t`` (the only degree‑1 vertices).  Removing the
leaf vertices and the edge ``[0, v_out]`` yields a Hamiltonian cycle in the
original graph, and conversely a Hamiltonian cycle can be turned into such a
path.  Hence the reduction is correct.

For source instances with ``n <= 2`` the answer is always *no* (by the problem
specification).  We map these to a trivially unsatisfiable Hamiltonian‑Path
instance (empty graph with ``n = 0``) so that the answers still match.
"""

from __future__ import annotations

from typing import List, Tuple

from problems import HamiltonianCycle, HamiltonianPath


def _add_edge(edge_set: set[Tuple[int, int]], u: int, v: int) -> None:
    """Add an undirected edge to *edge_set* in canonical order.

    ``edge_set`` stores edges as ``(min, max)`` tuples to avoid duplicates.
    """
    if u == v:
        return
    edge_set.add((min(u, v), max(u, v)))


def reduce(instance: dict) -> dict:
    """Reduce a Hamiltonian‑Cycle instance to a Hamiltonian‑Path instance.

    Returns a dict conforming to ``HamiltonianPath``'s instance format.
    """
    # Validate source instance.
    HamiltonianCycle.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Trivial NO cases.
    if n <= 2:
        return {"n": 0, "edges": []}

    # New vertices.
    v_out = n          # copy of original vertex 0
    s = n + 1          # leaf attached to original 0
    t = n + 2          # leaf attached to v_out
    new_n = n + 3

    new_edges: set[Tuple[int, int]] = set()

    # Core connections.
    _add_edge(new_edges, 0, v_out)  # connect original 0 and its copy
    _add_edge(new_edges, s, 0)      # leaf s
    _add_edge(new_edges, v_out, t)  # leaf t

    # Rewire edges incident to original vertex 0.
    for u, v in edges:
        if u == 0:
            _add_edge(new_edges, 0, v)
            _add_edge(new_edges, v_out, v)
        elif v == 0:
            _add_edge(new_edges, 0, u)
            _add_edge(new_edges, v_out, u)
        else:
            _add_edge(new_edges, u, v)

    edge_list = [[u, v] for (u, v) in new_edges]
    reduced_instance = {"n": new_n, "edges": edge_list}
    HamiltonianPath.validate(reduced_instance)
    return reduced_instance

