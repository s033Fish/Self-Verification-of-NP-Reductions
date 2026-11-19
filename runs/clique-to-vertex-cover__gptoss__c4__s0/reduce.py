"""Reduction from Clique to Vertex Cover.

The classic reduction uses the complement graph.  A set of vertices forms a
clique of size *k* in a graph *G* iff its complement (the vertices not in the
set) forms a vertex cover of size *n - k* in the complement graph *G̅*.

Given an instance of :class:`problems.Clique` we construct the instance of
``VertexCover`` with the same number of vertices, the complement edge set, and
``k' = n - k``.  This transformation preserves the answer for all edge cases:

* ``k <= 0`` → ``k' >= n`` → vertex‑cover instance is trivially a *yes* (k' ≥ n).
* ``k > n`` → ``k' < 0`` → vertex‑cover instance is trivially a *no* (k' < 0).
* Other values map correctly because a vertex cover of size ``n - k`` exists
  in the complement exactly when a clique of size ``k`` exists in the original.

The reduction runs in polynomial time – constructing the complement needs at
most O(n²) work.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import Clique, VertexCover


def _complement_edges(n: int, edges: List[List[int]]) -> List[List[int]]:
    """Return the edge list of the complement graph on ``n`` vertices.

    ``edges`` is assumed to be a valid edge list for an undirected simple
    graph (no self‑loops, no duplicate edges, each edge appears only once as a
    two‑element list ``[u, v]`` with ``u != v``).
    """
    # Store existing edges as an unordered pair set for O(1) membership.
    existing = {frozenset((u, v)) for u, v in edges}
    comp: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in existing:
                comp.append([u, v])
    return comp


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Clique instance to a VertexCover instance.

    The function validates the input using :class:`Clique.validate` and then
    constructs the complement graph.  The resulting instance is validated with
    :class:`VertexCover.validate` before being returned.
    """
    # Validate source instance.
    Clique.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Compute complement edge list.
    comp_edges = _complement_edges(n, edges)

    # New k for vertex cover.
    k_prime = n - k

    target_instance: Dict[str, Any] = {"n": n, "edges": comp_edges, "k": k_prime}

    # Validate target instance to catch any implementation mistakes.
    VertexCover.validate(target_instance)
    return target_instance

