"""Reduction from Hamiltonian Path to Hamiltonian Cycle.

The source problem is :class:`HamiltonianPath` (undirected graph, any
endpoints). The target problem is :class:`HamiltonianCycle` (undirected
graph, must form a cycle).  Both problems are defined in ``problems.py``.

We implement a polynomial‑time many‑one reduction ``reduce`` that maps a
source instance to a target instance such that the answer is preserved.

Standard reduction for ``n >= 3``:
    * Add a new vertex ``v_new`` (index ``n``) and connect it to **all**
      original vertices.
    * Any Hamiltonian cycle in the new graph must contain ``v_new``; removing
      it yields a Hamiltonian path in the original graph, and vice‑versa.

Small‑size edge cases need special handling because the target problem
declares that graphs with ``n <= 2`` are always *no*.

* ``n == 0`` – source is always *no*.  Return a 3‑vertex empty graph (no
  cycle).
* ``n == 1`` – source is always *yes*.  Return a triangle (3‑vertex complete
  graph) which always has a Hamiltonian cycle.
* ``n == 2`` – source is *yes* iff the edge ``[0, 1]`` exists.  Add a third
  vertex ``2`` adjacent to both ``0`` and ``1``.  The resulting graph is a
  triangle exactly when the original edge is present, otherwise it is a path
  of length two, which has no Hamiltonian cycle.

All other sizes use the generic construction.
"""

from __future__ import annotations

from typing import Any, Dict, List


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Map a Hamiltonian‑Path instance to a Hamiltonian‑Cycle instance.

    The returned instance follows the format required by
    :class:`HamiltonianCycle` – a dict with keys ``"n"`` and ``"edges"``.
    The transformation runs in O(|V|+|E|) time.
    """

    n: int = instance["n"]
    edges: List[List[int]] = [list(e) for e in instance["edges"]]

    # Helper to build the output dict.
    def make_output(num_vertices: int, edge_list: List[List[int]]) -> Dict[str, Any]:
        return {"n": num_vertices, "edges": edge_list}

    # n == 0 : source answer is always NO.  Return a graph with no Hamiltonian
    # cycle (e.g., three isolated vertices).
    if n == 0:
        return make_output(3, [])

    # n == 1 : source answer is always YES.  Return a triangle which always has
    # a Hamiltonian cycle.
    if n == 1:
        triangle = [[0, 1], [1, 2], [2, 0]]
        return make_output(3, triangle)

    # n == 2 : answer depends on the presence of edge [0,1].
    if n == 2:
        # Add a third vertex (index 2) adjacent to both original vertices.
        new_edges = edges.copy()
        new_edges.append([2, 0])
        new_edges.append([2, 1])
        return make_output(3, new_edges)

    # General case n >= 3.
    # Add a new vertex with index n and connect it to every original vertex.
    new_vertex = n
    new_edges = edges.copy()
    for v in range(n):
        new_edges.append([new_vertex, v])
    return make_output(n + 1, new_edges)

