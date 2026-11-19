"""Reduction from Clique to Independent Set.

The classic reduction uses the complement graph: a set of vertices forms a
clique in a graph G iff it forms an independent set in the complement of G.
Therefore we keep the number of vertices ``n`` and the target size ``k`` the
same, and replace the edge list with all non‑edges (excluding self‑loops).

The function ``reduce`` validates the source instance using ``Clique.validate``
and returns a new instance that conforms to ``IndependentSet``.  The returned
instance is guaranteed to be a yes‑instance of Independent Set exactly when
the original instance is a yes‑instance of Clique.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import Clique, IndependentSet


def _complement_edges(n: int, edges: List[List[int]]) -> List[List[int]]:
    """Return the edge list of the complement graph.

    ``edges`` is a list of undirected edges ``[u, v]`` with ``u != v`` and
    ``0 <= u, v < n``.  The complement contains every unordered pair of distinct
    vertices that is *not* present in ``edges``.
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

    The reduction runs in polynomial time: building the complement graph takes
    O(n^2) time, which is polynomial in the size of the input.
    """
    # Validate the source instance.  This will raise InvalidInstance if the
    # format is wrong.
    Clique.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Build the complement edge list.
    comp_edges = _complement_edges(n, edges)

    reduced_instance: Dict[str, Any] = {"n": n, "edges": comp_edges, "k": k}

    # Validate the target instance before returning to ensure we produced a
    # well‑formed IndependentSet instance.
    IndependentSet.validate(reduced_instance)
    return reduced_instance

