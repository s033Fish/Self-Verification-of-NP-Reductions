"""Reduction from Independent Set to Clique.

The classic reduction transforms an Independent Set instance (G, k) into a Clique
instance (\overline{G}, k), where \overline{G} is the complement of the input
graph. A set of vertices is independent in G iff it forms a clique in the
complement, so the answers are equivalent.

The ``reduce`` function validates the source instance using the ``IndependentSet``
class from ``problems.py`` and returns a dictionary that follows the ``Clique``
format.
"""

from __future__ import annotations

from typing import Dict, List, Set

from problems import IndependentSet, Clique


def _complement_edges(n: int, edges: List[List[int]]) -> List[List[int]]:
    """Compute the edge list of the complement graph.

    ``edges`` is a list of undirected edges ``[u, v]`` with ``u != v`` and
    ``0 <= u, v < n``. The complement contains exactly those unordered pairs
    that are not present in ``edges``.
    """
    # Store existing edges as frozensets for O(1) membership tests.
    existing: Set[frozenset[int]] = {frozenset(e) for e in edges}
    comp: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in existing:
                comp.append([u, v])
    return comp


def reduce(instance: Dict) -> Dict:
    """Reduce an Independent Set instance to a Clique instance.

    The returned instance has the same ``n`` and ``k`` as the input and its
    ``edges`` list is the complement of the input graph's edges.
    """
    # Validate the source instance – will raise InvalidInstance if malformed.
    IndependentSet.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    complement = _complement_edges(n, edges)

    target_instance: Dict = {"n": n, "edges": complement, "k": k}
    # Validate the produced instance to ensure correctness of the reduction.
    Clique.validate(target_instance)
    return target_instance

