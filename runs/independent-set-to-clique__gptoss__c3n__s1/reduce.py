"""Reduction from Independent Set to Clique.

The classic polynomial‑time reduction builds the complement graph:
for a given graph G = (V, E) we construct G' = (V, E') where
E' contains exactly those unordered pairs {u, v} (u != v) that are *not*
edges of G.  An independent set in G corresponds to a clique in G'.

The instance format for both problems is a dictionary with keys
"n", "edges" and "k" as described in ``problems.py``.  The ``reduce``
function validates the source instance, builds the complement graph, and
returns a target instance that satisfies ``Clique.validate``.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import IndependentSet, Clique


def _complement_edges(n: int, edges: List[List[int]]) -> List[List[int]]:
    """Return the edge list of the complement graph.

    ``edges`` is assumed to be a valid edge list for an undirected simple
    graph with vertices 0..n-1.  The result contains each unordered pair
    exactly once and never includes self‑loops.
    """
    # Build a set for quick lookup of existing edges.
    existing = {frozenset((u, v)) for u, v in (tuple(e) for e in edges)}
    comp: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in existing:
                comp.append([u, v])
    return comp


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Independent Set instance to a Clique instance.

    The reduction runs in O(n^2) time, which is polynomial in the size of the
    input instance.  It preserves the answer: the original instance has an
    independent set of size at least ``k`` iff the returned instance has a
    clique of size at least ``k``.
    """
    # Validate the source instance; raises InvalidInstance on malformed data.
    IndependentSet.validate(instance)

    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Build complement graph.
    comp_edges = _complement_edges(n, edges)

    target_instance: Dict[str, Any] = {"n": n, "edges": comp_edges, "k": k}
    # Ensure the produced instance is well‑formed for the target problem.
    Clique.validate(target_instance)
    return target_instance

