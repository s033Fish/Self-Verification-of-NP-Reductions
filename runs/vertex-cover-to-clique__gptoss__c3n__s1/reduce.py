"""Reduction from Vertex Cover to Clique.

The classic reduction uses the complement graph.  For a graph G=(V,E) and
an integer k, G has a vertex cover of size at most k iff the complement of G
has a clique of size at least |V|-k.

Given an instance of ``VertexCover`` we construct the complement graph and set
``k' = n - k``.  The returned instance is a valid ``Clique`` instance and the
answer to the two instances coincides.

The implementation runs in O(n^2) time which is polynomial in the size of the
input.
"""

from __future__ import annotations

from typing import List, Dict

from problems import VertexCover, Clique


def _edge_set(edges: List[List[int]]) -> set[frozenset[int]]:
    """Convert a list of ``[u, v]`` edges to a set of unordered pairs.

    The helper is used to test existence of an edge in O(1) time when building
    the complement.
    """
    return {frozenset((u, v)) for u, v in edges}


def reduce(instance: Dict) -> Dict:
    """Reduce a Vertex Cover instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary representing a Vertex Cover instance.  The function first
        validates the instance using ``VertexCover.validate``.

    Returns
    -------
    dict
        A dictionary representing a Clique instance that is the complement
        graph with ``k' = n - k``.
    """
    # Validate the source instance – this raises ``InvalidInstance`` on error.
    VertexCover.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Build the complement graph.
    original_edge_set = _edge_set(edges)
    complement_edges: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in original_edge_set:
                complement_edges.append([u, v])

    # New k for the Clique instance.
    new_k = n - k

    reduced_instance = {"n": n, "edges": complement_edges, "k": new_k}
    # Validate the target instance to guarantee correctness of the output.
    Clique.validate(reduced_instance)
    return reduced_instance

