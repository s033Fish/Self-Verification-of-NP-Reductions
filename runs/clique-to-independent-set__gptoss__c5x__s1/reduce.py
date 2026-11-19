"""Reduction from Clique to Independent Set.

The classic reduction maps a graph G to its complement G̅.  A set of vertices
forms a clique in G iff it forms an independent set in G̅, because every pair
of vertices that is *not* an edge in G becomes an edge in the complement and
vice‑versa.  Consequently we keep the vertex count ``n`` and the target size
``k`` unchanged and replace the edge list with its complement.

The function ``reduce`` takes a valid Clique instance (as defined in
``problems.py``) and returns a valid IndependentSet instance.  Validation is
performed using the problem classes' ``validate`` methods, which raise
``InvalidInstance`` on malformed input.
"""

from __future__ import annotations

from typing import Dict, List

from problems import Clique, IndependentSet


def _complement_edges(n: int, edges: List[List[int]]) -> List[List[int]]:
    """Compute the edge list of the complement graph.

    ``edges`` is a list of undirected edges, each represented as ``[u, v]``
    with ``u != v`` and ``0 <= u, v < n``.  The complement contains every
    unordered pair of distinct vertices that does **not** appear in ``edges``.
    """
    # Store existing edges in a set of frozensets for O(1) membership tests.
    existing = {frozenset((u, v)) for u, v in edges}
    comp: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in existing:
                comp.append([u, v])
    return comp


def reduce(instance: Dict) -> Dict:
    """Reduce a Clique instance to an Independent Set instance.

    The returned dictionary conforms to the format required by
    :class:`problems.IndependentSet`.  Validation is delegated to the problem
    classes – we simply construct a well‑formed instance.
    """
    # Validate the source instance; this raises InvalidInstance on bad input.
    Clique.validate(instance)

    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Compute complement edges.
    comp_edges = _complement_edges(n, edges)

    target_instance: Dict = {"n": n, "edges": comp_edges, "k": k}
    # Validate the produced target instance.
    IndependentSet.validate(target_instance)
    return target_instance

