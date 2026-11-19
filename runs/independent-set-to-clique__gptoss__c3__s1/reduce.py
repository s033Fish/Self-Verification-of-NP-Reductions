"""Reduction from Independent Set to Clique.

The classic reduction maps an instance \(G, k\) of Independent Set to the
instance \(\overline{G}, k\) of Clique, where \(\overline{G}\) is the
complement graph of \(G\).  An independent set in \(G\) corresponds exactly to
 a clique in the complement, and the parameter \(k\) is unchanged.

Both the source (IndependentSet) and target (Clique) problem classes are
defined in ``problems.py``.  The ``reduce`` function validates the source
instance, constructs the complement edge list, and returns a new instance in
the format required by the target problem.
"""

from __future__ import annotations

from typing import List, Dict, Any

import problems


def _complement_edges(n: int, edges: List[List[int]]) -> List[List[int]]:
    """Return the edge list of the complement of a simple undirected graph.

    ``edges`` is a list of ``[u, v]`` pairs with ``0 <= u, v < n`` and ``u != v``.
    The complement contains exactly those unordered pairs that are *not* in
    ``edges``.
    """
    # Store existing edges as frozensets for O(1) look‑up.
    existing = {frozenset(edge) for edge in edges}
    comp: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in existing:
                comp.append([u, v])
    return comp


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Independent Set instance to a Clique instance.

    The returned instance has the same ``n`` and ``k`` fields, and its edge
    list is the complement of the input graph.  The function runs in polynomial
    time (quadratic in ``n``) which satisfies the requirement.
    """
    # Validate the source instance using the provided problem class.
    problems.SOURCE.validate(instance)

    n = instance["n"]
    k = instance["k"]
    edges = instance["edges"]

    complement = _complement_edges(n, edges)

    reduced_instance = {"n": n, "edges": complement, "k": k}
    # Ensure the produced instance is a valid Clique instance.
    problems.TARGET.validate(reduced_instance)
    return reduced_instance

