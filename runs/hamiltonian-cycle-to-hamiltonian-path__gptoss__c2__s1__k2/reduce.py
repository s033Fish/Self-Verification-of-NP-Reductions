"""Reduction from Hamiltonian Cycle to Hamiltonian Path.

The source problem (HamiltonianCycle) expects an instance of the form::

    {"n": n, "edges": [[u, v], ...]}

where vertices are ``0..n-1`` and each edge is an undirected pair ``[u, v]``.

The target problem (HamiltonianPath) uses the same format.  The reduction
produces a new graph ``G'`` such that ``G`` has a Hamiltonian *cycle* iff ``G'``
has a Hamiltonian *path*.

Construction (standard many‑one reduction):

* Create two copies of the original vertex set:
  - copy‑0 vertices are ``0 .. n-1``
  - copy‑1 vertices are ``n .. 2*n-1`` (offset by ``n``)
* Add a new start vertex ``s = 2*n`` and a new terminal vertex ``t = 2*n+1``.
* For each original edge ``(u, v)`` add the following undirected edges to ``G'``:
  - ``(u, v)``            – the edge inside copy‑0
  - ``(u+n, v+n)``        – the edge inside copy‑1
  - ``(u, v+n)`` and ``(v, u+n)`` – the crossing edges.
* Connect ``s`` to every vertex of copy‑0 and connect ``t`` to every vertex of
  copy‑1.

The resulting graph has ``2*n + 2`` vertices.  Any Hamiltonian path in ``G'``
must start at ``s``, traverse all vertices of copy‑0, cross to copy‑1 via a
crossing edge that corresponds to some original edge ``(a, b)``, traverse all
vertices of copy‑1, and finish at ``t``.  The order of traversal inside each
copy yields a Hamiltonian cycle in the original graph, and the construction
is reversible.

The implementation below follows this construction and runs in polynomial
time.
"""

from __future__ import annotations

from typing import List, Dict, Any


def _add_edge(edges: List[List[int]], u: int, v: int) -> None:
    """Add an undirected edge ``[u, v]`` to ``edges`` ensuring ``u < v``.

    The source/target specifications require each edge to appear exactly once
    with the smaller endpoint first.  Duplicate edges are ignored because the
    reduction never generates the same unordered pair twice.
    """
    if u > v:
        u, v = v, u
    edges.append([u, v])


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Hamiltonian‑Cycle instance to a Hamiltonian‑Path instance.

    Parameters
    ----------
    instance:
        Dictionary with keys ``"n"`` (int) and ``"edges"`` (list of ``[u, v]``).

    Returns
    -------
    dict
        An instance of the Hamiltonian‑Path problem satisfying the required
        equivalence.
    """
    n: int = instance["n"]
    original_edges: List[List[int]] = instance["edges"]

    # The source problem is defined to be a NO instance for n <= 2.
    # To preserve the equivalence we return a trivially NO Hamiltonian‑Path
    # instance (n = 0 has no path).
    if n <= 2:
        return {"n": 0, "edges": []}

    # New graph parameters for the general case (n >= 3)
    new_n = 2 * n + 2
    s = 2 * n      # start vertex
    t = 2 * n + 1  # terminal vertex

    new_edges: List[List[int]] = []

    # Add edges inside each copy and the crossing edges.
    for u, v in original_edges:
        # edges inside copy‑0
        _add_edge(new_edges, u, v)
        # edges inside copy‑1 (offset by n)
        _add_edge(new_edges, u + n, v + n)
        # crossing edges corresponding to the original edge
        _add_edge(new_edges, u, v + n)
        _add_edge(new_edges, v, u + n)

    # Connect s to all vertices of copy‑0
    for v in range(n):
        _add_edge(new_edges, s, v)

    # Connect t to all vertices of copy‑1
    for v in range(n):
        _add_edge(new_edges, t, v + n)

    return {"n": new_n, "edges": new_edges}

