"""Reduction from Vertex Cover to Clique.

Given an instance of Vertex Cover (graph G with n vertices, edge list, and integer k),
the reduction constructs the complement graph G̅ (same vertex set, edge between
u and v iff {u,v} is *not* an edge of G and u != v) and asks whether G̅ contains a
clique of size at least n - k.

The standard theorem states:
    G has a vertex cover of size ≤ k   ⇔   G̅ has a clique of size ≥ n‑k.

This reduction runs in polynomial time (O(n^2) to build the complement) and
preserves the answer for all edge‑cases described in the problem statements.
"""

from __future__ import annotations

from typing import Dict, List

from problems import VertexCover, Clique


def complement_edges(n: int, edges: List[List[int]]) -> List[List[int]]:
    """Return the edge list of the complement graph.

    The complement contains an edge {u,v} for every unordered pair of distinct
    vertices that is *not* present in ``edges``.
    """
    # Build a set of existing edges for O(1) lookup.
    existing = {frozenset((u, v)) for u, v in edges}
    comp: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in existing:
                comp.append([u, v])
    return comp


def reduce(instance: Dict) -> Dict:
    """Reduce a VertexCover instance to a Clique instance.

    Parameters
    ----------
    instance: dict
        Must satisfy ``VertexCover.validate``.

    Returns
    -------
    dict
        An instance of the Clique problem such that the answer is yes exactly
        when the original VertexCover instance is yes.
    """
    # Validate the source instance.
    VertexCover.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Complement graph edges.
    comp_edges = complement_edges(n, edges)

    # Target k is n - k (size of the desired clique).
    target_k = n - k

    # Build the target instance.
    target_instance: Dict = {"n": n, "edges": comp_edges, "k": target_k}

    # Validate the target instance (should always succeed).
    Clique.validate(target_instance)
    return target_instance

