"""Reduction from Hamiltonian Cycle to Hamiltonian Path.

The source problem is *Hamiltonian Cycle* (undirected) with instance format:
    {"n": n, "edges": [[u, v], ...]}
The target problem is *Hamiltonian Path* (undirected, any endpoints) with the
same format.

We implement a classic polynomial‑time many‑one reduction.  For a graph G
with at least three vertices we split an arbitrary vertex (we choose vertex
0) into two vertices ``a`` and ``b`` and attach two new pendant vertices
``s`` and ``t`` to ``a`` and ``b`` respectively.  The construction forces any
Hamiltonian path in the new graph to start at ``s`` and end at ``t``.  Removing
``s``, ``t`` and merging ``a``/``b`` back into the original vertex yields a
Hamiltonian cycle in G, and conversely a Hamiltonian cycle in G can be broken
at vertex 0 to obtain a Hamiltonian path from ``s`` to ``t`` in the constructed
graph.

For the trivial source instances with ``n <= 2`` the answer is always *no* for
Hamiltonian Cycle, so we return a target instance that is also a definite *no*
instance (``n = 0``).

The reduction runs in O(n + m) time and produces a graph with ``n + 4``
vertices.
"""

from __future__ import annotations

from typing import List, Dict, Tuple, Set


def _add_edge(edges_set: Set[Tuple[int, int]], u: int, v: int) -> None:
    """Add an undirected edge to the set, storing the ordered tuple (min, max)."""
    if u == v:
        # self‑loops are not allowed in the problem definitions.
        return
    a, b = (u, v) if u < v else (v, u)
    edges_set.add((a, b))


def reduce(instance: Dict) -> Dict:
    """Reduce a Hamiltonian‑Cycle instance to a Hamiltonian‑Path instance.

    Parameters
    ----------
    instance: dict
        ``{"n": int, "edges": [[u, v], ...]}`` describing an undirected graph.

    Returns
    -------
    dict
        An instance of the Hamiltonian‑Path problem with the property that
        the answer is *yes* iff the original instance is *yes*.
    """
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Trivial cases: source is always NO for n <= 2, so return a definite NO.
    if n <= 2:
        return {"n": 0, "edges": []}

    # New vertex identifiers.
    a_id = n          # split copy 1 of vertex 0
    b_id = n + 1      # split copy 2 of vertex 0
    s_id = n + 2      # pendant attached to a_id
    t_id = n + 3      # pendant attached to b_id
    new_n = n + 4

    new_edges_set: Set[Tuple[int, int]] = set()

    # Preserve edges that do not involve vertex 0.
    for u, v in edges:
        if 0 not in (u, v):
            _add_edge(new_edges_set, u, v)

    # Replace each edge incident to vertex 0 with edges to both a_id and b_id.
    for u, v in edges:
        if u == 0 and v != 0:
            x = v
            _add_edge(new_edges_set, a_id, x)
            _add_edge(new_edges_set, b_id, x)
        elif v == 0 and u != 0:
            x = u
            _add_edge(new_edges_set, a_id, x)
            _add_edge(new_edges_set, b_id, x)
        # The case (0,0) cannot happen by problem definition.

    # Add the two pendant edges.
    _add_edge(new_edges_set, s_id, a_id)
    _add_edge(new_edges_set, t_id, b_id)

    # Convert set back to list of lists.
    new_edges: List[List[int]] = [[u, v] for (u, v) in new_edges_set]

    return {"n": new_n, "edges": new_edges}

