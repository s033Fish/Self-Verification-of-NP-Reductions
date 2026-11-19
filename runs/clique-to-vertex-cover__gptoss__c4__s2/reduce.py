"""Reduction from Clique to Vertex Cover.

The classic polynomial‑time reduction uses the complement graph:
    G has a clique of size k  <=>  the complement of G has a vertex cover
    of size n - k.

Both problems share the same instance format (undirected simple graph with
integer parameter k).  The reduction therefore constructs the complement
graph and adjusts the parameter accordingly.

The function ``reduce`` validates the source instance using ``Clique.validate``
and returns a new instance that satisfies ``VertexCover.validate``.  The
returned instance has the same number of vertices, the complement edge set,
and ``k' = n - k``.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import Clique, VertexCover


def complement_edges(n: int, edges: List[List[int]]) -> List[List[int]]:
    """Return the edge list of the complement graph of an undirected simple graph.

    The input ``edges`` is assumed to be a list of unordered pairs ``[u, v]``
    with ``0 <= u < v < n`` and no duplicates.  The complement contains exactly
    those unordered pairs that are *not* present in ``edges``.
    """
    # Build a set of frozensets for O(1) membership tests.
    present = {frozenset(edge) for edge in edges}
    comp: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in present:
                comp.append([u, v])
    return comp


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Clique instance to an equivalent VertexCover instance.

    Parameters
    ----------
    instance:
        A dictionary representing a Clique instance as described in
        ``problems.Clique``.

    Returns
    -------
    dict
        A VertexCover instance with the same vertex set, the complement edge
        set, and ``k' = n - k``.
    """
    # Validate the source instance; will raise InvalidInstance on malformed input.
    Clique.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Construct complement graph and adjust k.
    comp_edges = complement_edges(n, edges)
    k_prime = n - k

    reduced_instance: Dict[str, Any] = {
        "n": n,
        "edges": comp_edges,
        "k": k_prime,
    }

    # Ensure the produced instance is well‑formed for VertexCover.
    VertexCover.validate(reduced_instance)
    return reduced_instance

