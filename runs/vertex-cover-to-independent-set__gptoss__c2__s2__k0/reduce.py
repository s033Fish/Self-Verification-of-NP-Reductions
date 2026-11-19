"""Reduction from Vertex Cover to Independent Set.

The source problem (VertexCover) asks whether a graph G = (V, E) has a
vertex cover of size at most *k*.  The target problem (IndependentSet) asks
whether G has an independent set of size at least *k'*.

For any graph the complement of a vertex cover is an independent set:

    S is a vertex cover  <=>  V \ S is an independent set.

Consequently, G has a vertex cover of size ≤ k iff it has an independent set
of size ≥ |V| − k.  The reduction therefore keeps the graph unchanged and
maps the parameter *k* to *k' = n - k* where *n* is the number of vertices.

This transformation is clearly polynomial‑time (linear in the size of the
instance) and preserves the answer for all edge cases described in the
problem statements:

* k < 0  →  n - k > n, which is a guaranteed *no* for Independent Set.
* k ≥ n  →  n - k ≤ 0, which is a guaranteed *yes* for Independent Set.
* Empty edge set works trivially because the graph is unchanged.

The function ``reduce`` implements this mapping.  It does not perform any
validation or call the solvers – it merely constructs the new instance.
"""

from __future__ import annotations

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a VertexCover instance to an IndependentSet instance.

    Parameters
    ----------
    instance:
        A dictionary representing a VertexCover instance with keys
        ``"n"`` (int), ``"edges"`` (list of [u, v] pairs), and ``"k"`` (int).

    Returns
    -------
    dict
        A dictionary representing an IndependentSet instance with the same
        vertices and edges, and with ``k`` transformed to ``n - k``.
    """

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # The reduction keeps the graph unchanged; we make a shallow copy of the
    # edge list to avoid accidental mutation of the original instance.
    new_edges = [list(e) for e in edges]

    new_k = n - k

    return {"n": n, "edges": new_edges, "k": new_k}
