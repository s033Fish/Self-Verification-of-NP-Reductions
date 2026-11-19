"""Reduction from Independent Set to Clique.

The classic reduction uses the complement graph: an independent set in a
graph G corresponds exactly to a clique in the complement of G.  This file
exposes a single function ``reduce`` that takes a valid Independent Set
instance and returns a valid Clique instance with the same number of
vertices and the same target size ``k``.

Both the source and target problem definitions live in ``problems.py``.
The function validates the input using ``IndependentSet.validate`` and the
output using ``Clique.validate`` to guarantee that the returned instance
conforms to the specification.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import IndependentSet, Clique


def _complement_edges(n: int, edges: List[List[int]]) -> List[List[int]]:
    """Return the edge list of the complement graph.

    The complement contains exactly those unordered vertex pairs ``{u, v}``
    with ``u != v`` that are *not* present in ``edges``.
    The input ``edges`` is assumed to be a list of two‑element lists as
    required by the problem definitions.
    """
    # Store existing edges in a set of frozensets for O(1) look‑ups.
    existing = {frozenset((u, v)) for u, v in edges}
    comp: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in existing:
                comp.append([u, v])
    return comp


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Independent Set instance to a Clique instance.

    The reduction is polynomial‑time: we simply compute the complement of the
    input graph, which takes O(n^2) time.
    """
    # Validate the source instance first – this will raise ``InvalidInstance``
    # if the instance is malformed.
    IndependentSet.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Build the complement graph.
    complement = _complement_edges(n, edges)

    # Construct the target instance.
    target_instance: Dict[str, Any] = {"n": n, "edges": complement, "k": k}

    # Validate the produced instance to guarantee correctness of the format.
    Clique.validate(target_instance)
    return target_instance

