"""Reduction from Clique to Independent Set.

The reduction is the classic complement‑graph construction:

* Input: an instance of :class:`Clique` – a graph ``G = (V, E)`` and an
  integer ``k``.
* Output: an instance of :class:`IndependentSet`` – the same vertex set ``V``
  and the *complement* edge set ``E' = {{u, v} | u != v, {u, v} \notin E}``.

A set of vertices forms a clique in ``G`` iff it forms an independent set in
the complement graph. Consequently, ``G`` contains a clique of size at least
``k`` exactly when the complement contains an independent set of size at least
``k``. Edge‑case handling (``k <= 0``, ``k = 1`` and ``k > n``) is preserved
automatically because the reduction does not modify ``k`` or the number of
vertices.

The ``reduce`` function validates the source instance, builds the complement
graph, and returns a new instance suitable for the target problem.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import Clique, IndependentSet


def _complement_edges(n: int, edges: List[List[int]]) -> List[List[int]]:
    """Return the edge list of the complement of a simple undirected graph.

    Parameters
    ----------
    n:
        Number of vertices (vertices are ``0..n-1``).
    edges:
        List of edges ``[u, v]`` where ``u != v`` and each unordered pair appears
        at most once.

    Returns
    -------
    List[List[int]]
        Edge list of the complement graph – all unordered pairs that are *not*
        present in ``edges``.
    """
    # Store existing edges in a set of frozensets for O(1) look‑ups.
    existing = {frozenset((u, v)) for u, v in edges}
    complement: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in existing:
                complement.append([u, v])
    return complement


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Clique instance to an Independent‑Set instance.

    The function runs in polynomial time (quadratic in ``n``) and preserves the
    answer of the original instance.
    """
    # Validate source instance – will raise InvalidInstance if malformed.
    Clique.validate(instance)

    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Build complement graph.
    comp_edges = _complement_edges(n, edges)

    # Construct target instance. Validation of the target will be performed by
    # the caller if needed.
    target_instance: Dict[str, Any] = {"n": n, "edges": comp_edges, "k": k}
    # Optionally validate the target to catch programming errors early.
    IndependentSet.validate(target_instance)
    return target_instance

