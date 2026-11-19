"""Reduction from Clique to Independent Set.

The classic reduction complements the input graph: a set of vertices forms a
clique in the original graph *G* iff it forms an independent set in the
complement graph *G̅* (the graph containing exactly the non‑edges of *G*).

The instance format for both problems is a dictionary with keys ``n``,
``edges`` and ``k`` as described in ``problems.py``.  The reduction therefore
keeps ``n`` and ``k`` unchanged and replaces the edge list with its complement.

The function validates the input using ``Clique.validate`` and validates the
output using ``IndependentSet.validate`` before returning it.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import Clique, IndependentSet


def _complement_edges(n: int, edges: List[List[int]]) -> List[List[int]]:
    """Return the edge list of the complement of an undirected simple graph.

    ``edges`` is assumed to contain each undirected edge exactly once as a
    two‑element list ``[u, v]`` with ``u != v`` and ``0 <= u, v < n``.  The
    complement contains all unordered pairs ``{u, v}`` that are *not* present
    in ``edges``.
    """
    # Use a set of frozensets for O(1) membership checks.
    present = {frozenset((u, v)) for u, v in edges}
    comp: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in present:
                comp.append([u, v])
    return comp


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Clique instance to an Independent Set instance.

    The returned instance has the same ``n`` and ``k`` and its edge list is the
    complement of the original graph.  The transformation runs in O(n²) time,
    which is polynomial in the size of the input.
    """
    # Validate the source instance.
    Clique.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    comp_edges = _complement_edges(n, edges)
    reduced_instance: Dict[str, Any] = {"n": n, "edges": comp_edges, "k": k}

    # Validate the target instance before returning.
    IndependentSet.validate(reduced_instance)
    return reduced_instance

