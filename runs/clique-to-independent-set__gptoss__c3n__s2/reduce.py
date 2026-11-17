"""Reduction from Clique to Independent Set.

The source problem is :class:`problems.Clique` and the target problem is
``IndependentSet``.  The classic polynomial‑time many‑one reduction uses the
graph complement: a set of vertices is a clique in ``G`` iff it is an
independent set in the complement of ``G``.

The reduction therefore keeps the number of vertices ``n`` and the required
size ``k`` unchanged and replaces the edge list with the complement edge list.

The function :func:`reduce` validates the input instance using the source
problem's ``validate`` method, constructs the complement graph, validates the
produced instance with the target problem's ``validate`` method and returns it.
"""

from __future__ import annotations

from typing import List, Dict, Any

import problems


def _complement_edges(n: int, edges: List[List[int]]) -> List[List[int]]:
    """Return the edge list of the complement of a simple undirected graph.

    ``edges`` is assumed to be a list of ``[u, v]`` where ``0 <= u, v < n`` and
    ``u != v``.  The complement contains exactly those unordered pairs that are
    *not* present in ``edges``.
    """
    existing = {frozenset((u, v)) for u, v in edges}
    comp: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in existing:
                comp.append([u, v])
    return comp


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Clique instance to an Independent Set instance.

    The returned instance has the same ``n`` and ``k`` as the input and its
    edge list is the complement of the input edge list.
    """
    problems.Clique.validate(instance)
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]
    comp_edges = _complement_edges(n, edges)
    reduced_instance: Dict[str, Any] = {"n": n, "edges": comp_edges, "k": k}
    problems.IndependentSet.validate(reduced_instance)
    return reduced_instance

