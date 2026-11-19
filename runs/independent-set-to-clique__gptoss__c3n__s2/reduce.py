"""Reduction from Independent Set to Clique.

The classic reduction uses the complement graph: an independent set in a
graph G corresponds exactly to a clique in the complement of G.  This file
provides a single function ``reduce`` that takes a valid Independent Set
instance (as defined in ``problems.py``) and returns a Clique instance that
has the same answer.

Both the source and target formats are plain dictionaries with the keys
``"n"``, ``"edges"`` and ``"k"``.  The reduction therefore keeps the number
of vertices ``n`` and the target size ``k`` unchanged and constructs the
edge set of the complement graph.
"""

from __future__ import annotations

from typing import List, Dict, Any

# Import the problem classes for validation.
from problems import IndependentSet, Clique


def _complement_edges(n: int, edges: List[List[int]]) -> List[List[int]]:
    """Return the edge list of the complement of a simple undirected graph.

    ``edges`` is a list of ``[u, v]`` with ``0 <= u < v < n`` and no duplicates.
    The complement contains exactly those unordered pairs that are *not*
    present in ``edges``.
    """
    # Store existing edges in a set of frozensets for O(1) lookup.
    existing = {frozenset((u, v)) for u, v in edges}
    comp: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in existing:
                comp.append([u, v])
    return comp


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Independent Set instance to a Clique instance.

    The returned instance has the same ``n`` and ``k``.  Its edge list is the
    complement of the original graph.  The function validates the input using
    ``IndependentSet.validate`` and ensures the output conforms to the Clique
    format by calling ``Clique.validate`` before returning.
    """
    # Validate the source instance.
    IndependentSet.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Build the complement graph.
    comp_edges = _complement_edges(n, edges)

    reduced_instance: Dict[str, Any] = {"n": n, "edges": comp_edges, "k": k}

    # Validate the target instance (will raise if something is wrong).
    Clique.validate(reduced_instance)
    return reduced_instance

