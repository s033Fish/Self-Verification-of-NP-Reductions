"""Reduction from Clique to Vertex Cover.

Given an instance of the Clique problem {"n": n, "edges": [...], "k": k}
we produce an instance of VertexCover on the complement graph with parameter
``k' = n - k``.  The classic graph‑theoretic relationship states:

    G has a clique of size at least k  <=>  the complement of G has a vertex
    cover of size at most n - k.

The reduction runs in polynomial time: constructing the complement requires
O(n^2) time and the rest is O(1).

The function validates the input using ``Clique.validate`` and returns a
dictionary that conforms to the ``VertexCover`` instance format.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import Clique, VertexCover


def _complement_edges(n: int, edges: List[List[int]]) -> List[List[int]]:
    """Return the edge list of the complement of a simple undirected graph.

    The input ``edges`` is assumed to be a valid edge list (no duplicates,
    undirected, no self‑loops).  The output list contains each unordered pair
    ``[u, v]`` with ``0 <= u < v < n`` that is *not* present in ``edges``.
    """
    # Create a set of frozensets for O(1) membership tests.
    existing = {frozenset(edge) for edge in edges}
    comp: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in existing:
                comp.append([u, v])
    return comp


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Clique instance to a VertexCover instance.

    Parameters
    ----------
    instance:
        A dictionary representing a Clique instance.  It must pass
        ``Clique.validate``.

    Returns
    -------
    dict
        A VertexCover instance {"n": n, "edges": complement, "k": n - k}.
    """
    # Validate the source instance.
    Clique.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Build the complement graph.
    comp_edges = _complement_edges(n, edges)

    # Parameter transformation.
    k_target = n - k

    # Assemble the target instance.
    target_instance: Dict[str, Any] = {"n": n, "edges": comp_edges, "k": k_target}

    # Validate the produced instance against the VertexCover definition.
    VertexCover.validate(target_instance)
    return target_instance

