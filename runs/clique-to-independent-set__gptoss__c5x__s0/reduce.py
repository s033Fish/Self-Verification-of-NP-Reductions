"""Reduction from Clique to Independent Set.

The source problem is :class:`Clique` and the target problem is
``IndependentSet``.  The classic polynomial‑time reduction is to take the
complement graph.  A set of vertices forms a clique in ``G`` iff it forms an
independent set in the complement ``\bar G``.  The reduction therefore keeps the
number of vertices ``n`` and the required size ``k`` unchanged and replaces the
edge list with all non‑edges of the original graph.

The function ``reduce`` validates the source instance using the provided
``Clique.validate`` method, constructs the complement edge list, validates the
resulting target instance with ``IndependentSet.validate`` and returns it.

The implementation runs in ``O(n^2)`` time which is polynomial in the size of
the input instance.
"""

from __future__ import annotations

from typing import List, Dict, Any, Set

from problems import Clique, IndependentSet


def _complement_edges(n: int, edges: List[List[int]]) -> List[List[int]]:
    """Return the edge list of the complement graph.

    ``edges`` is assumed to be a list of undirected edges where each edge is a
    two‑element list ``[u, v]`` with ``u != v`` and ``0 <= u, v < n``.  The
    complement contains exactly those unordered pairs that are *not* present in
    ``edges``.
    """
    # Store existing edges in a set of frozensets for O(1) look‑ups.
    present: Set[frozenset[int]] = {frozenset(e) for e in edges}
    comp: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in present:
                comp.append([u, v])
    return comp


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a ``Clique`` instance to an ``IndependentSet`` instance.

    The returned instance has the same ``n`` and ``k`` and its edge list is the
    complement of the original graph.
    """
    # Validate the source instance – this will raise InvalidInstance on bad
    # input, matching the behaviour of the original problem definitions.
    Clique.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    complement = _complement_edges(n, edges)
    target_instance: Dict[str, Any] = {"n": n, "edges": complement, "k": k}

    # Validate the produced target instance to guarantee correctness of the
    # reduction implementation itself.
    IndependentSet.validate(target_instance)
    return target_instance

