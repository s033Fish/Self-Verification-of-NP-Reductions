"""Reduction from Independent Set to Clique.

Given an instance of Independent Set (a graph G and an integer k), the
reduction constructs the complement graph \(\overline{G}\) and keeps the same
parameter k.  An independent set of size at least k in G is exactly a clique of
size at least k in \(\overline{G}\).

The function validates the source instance using ``IndependentSet.validate``
and returns a dictionary that conforms to the ``Clique`` problem definition.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import IndependentSet, Clique


def _complement_edges(n: int, edges: List[List[int]]) -> List[List[int]]:
    """Return the edge list of the complement of an undirected simple graph.

    ``edges`` is a list of ``[u, v]`` with ``0 <= u, v < n`` and ``u != v``.
    The complement contains exactly those unordered pairs that are **not**
    present in ``edges``.
    """
    existing = {frozenset((u, v)) for u, v in edges}
    comp: List[List[int]] = []
    for i in range(n):
        for j in range(i + 1, n):
            if frozenset((i, j)) not in existing:
                comp.append([i, j])
    return comp


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Independent Set instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the ``IndependentSet`` format.

    Returns
    -------
    dict
        A dictionary adhering to the ``Clique`` format such that the answer
        (yes/no) is preserved.
    """
    # Validate the source instance first – this will raise ``InvalidInstance``
    # if the input is malformed.
    IndependentSet.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Build the complement graph.
    comp_edges = _complement_edges(n, edges)

    target_instance: Dict[str, Any] = {"n": n, "edges": comp_edges, "k": k}

    # Validate the produced target instance to guarantee it respects the
    # Clique specification.
    Clique.validate(target_instance)
    return target_instance
