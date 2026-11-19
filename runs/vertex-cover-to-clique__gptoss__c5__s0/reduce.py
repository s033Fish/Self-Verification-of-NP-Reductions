"""Reduction from Vertex Cover to Clique.

The source problem is ``VertexCover`` as defined in ``problems.py``.  An
instance is a dictionary ``{"n": n, "edges": [[u, v], ...], "k": k}``.

The target problem is ``Clique`` with the same instance format.

The classic polynomial‑time reduction uses the complement graph.  A set
``S`` is a vertex cover of size at most ``k`` in a graph ``G`` iff the
remaining vertices ``V \ S`` form an independent set of size at least
``n - k``.  Independent sets in ``G`` correspond to cliques in the complement
graph ``G̅``.  Therefore ``G`` has a vertex cover of size ≤ ``k`` iff the
complement graph has a clique of size ≥ ``n - k``.

This file provides a single function ``reduce(instance)`` that performs the
transformation.  It validates the source instance, builds the complement edge
list, and returns a target instance that satisfies the above equivalence.
"""

from __future__ import annotations

from typing import List, Dict, Any, Set, Tuple

from problems import VertexCover, Clique


def _edge_key(u: int, v: int) -> Tuple[int, int]:
    """Return a canonical representation of an undirected edge.

    The reduction stores edges as a set of ordered tuples ``(min, max)`` to
    guarantee uniqueness and allow O(1) membership tests.
    """

    return (u, v) if u < v else (v, u)


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Vertex‑Cover instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary representing a VertexCover instance.  It is validated
        using ``VertexCover.validate``.

    Returns
    -------
    dict
        A Clique instance ``{"n": n, "edges": [...], "k": n - k_src}`` where
        the edge list is the complement of the original graph.
    """

    # Validate the source instance – this raises ``InvalidInstance`` if the
    # format is incorrect.
    VertexCover.validate(instance)

    n: int = instance["n"]
    edges_src: List[List[int]] = instance["edges"]
    k_src: int = instance["k"]

    # Build a set of existing edges for O(1) look‑up.
    existing: Set[Tuple[int, int]] = set()
    for u, v in edges_src:
        existing.add(_edge_key(u, v))

    # Construct the complement edge list.
    complement_edges: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if _edge_key(u, v) not in existing:
                complement_edges.append([u, v])

    # The target k is n - k_src as explained in the reduction proof.
    k_target: int = n - k_src

    target_instance: Dict[str, Any] = {
        "n": n,
        "edges": complement_edges,
        "k": k_target,
    }

    # Validate the produced target instance to catch any programming error.
    Clique.validate(target_instance)

    return target_instance

