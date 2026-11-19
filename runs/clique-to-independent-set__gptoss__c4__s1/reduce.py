"""Reduction from Clique to Independent Set.

The classic reduction uses the complement graph: a set of vertices forms a
clique in a graph G iff it forms an independent set in the complement of G.

Given an instance of the ``Clique`` problem (a graph ``G`` with parameters
``n``, ``edges`` and an integer ``k``) we construct an instance of the
``IndependentSet`` problem on the complement graph ``G'`` with the same ``k``.

The function ``reduce`` performs this transformation and runs in polynomial
time with respect to the size of the input (O(n^2) to enumerate all possible
edges).  The output instance satisfies the validation rules of
``IndependentSet``.
"""

from __future__ import annotations

from typing import List, Dict, Any, Set

from problems import Clique, IndependentSet, InvalidInstance


def _complement_edges(n: int, edges: List[List[int]]) -> List[List[int]]:
    """Return the edge list of the complement graph.

    The complement contains exactly those unordered pairs ``{u, v}`` with
    ``0 <= u < v < n`` that are *not* present in ``edges``.
    """
    # Store existing edges in a set of frozensets for O(1) lookup.
    existing: Set[frozenset[int]] = {frozenset(e) for e in edges}
    comp: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in existing:
                comp.append([u, v])
    return comp


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Clique instance to an IndependentSet instance.

    Parameters
    ----------
    instance:
        A dictionary representing a Clique instance. It must pass
        ``Clique.validate``.

    Returns
    -------
    dict
        A dictionary representing an IndependentSet instance which is the
        complement graph of the input and uses the same ``k``.
    """
    # Validate the source instance first – this will raise InvalidInstance if
    # the input is malformed.
    Clique.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Compute complement edges.
    comp_edges = _complement_edges(n, edges)

    reduced_instance: Dict[str, Any] = {"n": n, "edges": comp_edges, "k": k}

    # Ensure the produced instance is valid for the target problem.
    IndependentSet.validate(reduced_instance)

    return reduced_instance

