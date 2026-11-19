"""Reduction from Vertex Cover to Clique.

The reduction is the classic complement‑graph construction:

* Given a graph G = (V, E) and an integer k, we build the complement
  graph G̅ = (V, \overline{E}) where (u, v) is an edge of G̅ iff u ≠ v and
  (u, v) ∉ E.
* A set S ⊆ V is a vertex cover of G of size ≤ k iff the complement set
  V \ S is an independent set of size ≥ |V| - k in G.  An independent set in
  G corresponds exactly to a clique in the complement graph G̅.

Therefore G has a vertex cover of size at most k **iff** G̅ has a clique of
size at least |V| - k.

The function ``reduce`` validates the source instance, constructs the complement
graph, and returns a target instance for the Clique problem.
"""

from __future__ import annotations

from typing import Dict, List

from problems import VertexCover, Clique


def _complement_edges(n: int, edges: List[List[int]]) -> List[List[int]]:
    """Return the edge list of the complement graph.

    The returned list contains each unordered edge exactly once as ``[u, v]``
    with ``u < v``.  The input ``edges`` is assumed to be a valid edge list for
    a simple undirected graph (no duplicates, no self‑loops).
    """
    # Build a set of frozensets for O(1) membership tests.
    existing = {frozenset((u, v)) for u, v in edges}
    comp: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in existing:
                comp.append([u, v])
    return comp


def reduce(instance: Dict) -> Dict:
    """Reduce a Vertex Cover instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary describing a Vertex Cover instance as defined in
        ``problems.VertexCover``.

    Returns
    -------
    dict
        A Clique instance that is equivalent with respect to the yes‑answer.
    """
    # Validate the source instance – will raise InvalidInstance on malformed input.
    VertexCover.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Complement graph edges.
    comp_edges = _complement_edges(n, edges)

    # Target k is |V| - k (may be negative or exceed n – handled by Clique's edge
    # cases).
    target_k = n - k

    target_instance: Dict = {"n": n, "edges": comp_edges, "k": target_k}

    # Validate the produced target instance to ensure we obey the format.
    Clique.validate(target_instance)
    return target_instance

