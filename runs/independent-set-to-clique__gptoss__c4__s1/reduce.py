"""Reduction from Independent Set to Clique.

The standard polynomial‑time reduction builds the complement graph:
an independent set in a graph G corresponds exactly to a clique of the same
size in the complement of G (the graph with the same vertex set and an edge
between two vertices iff G does *not* have that edge).

The source problem is :class:`IndependentSet` and the target problem is
``Clique``. Both use the same instance format – a dict with keys ``n``,
``edges`` and ``k`` – so the reduction simply returns a new dict with the
complement edges and the same ``n`` and ``k``.

The function validates the input using the problem class' ``validate``
method (which raises :class:`InvalidInstance` on malformed data) and then
constructs the complement edge list in O(n^2) time, which is polynomial.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import IndependentSet, Clique, InvalidInstance


def _complement_edges(n: int, edges: List[List[int]]) -> List[List[int]]:
    """Return the edge list of the complement of an undirected graph.

    ``edges`` is assumed to be a list of unordered pairs ``[u, v]`` with
    ``0 <= u < v < n`` (the validation in ``problems.py`` guarantees this).
    The complement contains exactly those pairs that are *not* present.
    """
    # Store existing edges in a set of frozensets for O(1) lookup.
    present = {frozenset(edge) for edge in edges}
    comp: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in present:
                comp.append([u, v])
    return comp


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Independent Set instance to a Clique instance.

    The returned instance has the same ``n`` and ``k`` and edges equal to the
    complement of the original graph. The function runs in O(n^2) time.
    """
    # Validate the source instance – will raise InvalidInstance if malformed.
    IndependentSet.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Build the complement graph.
    comp_edges = _complement_edges(n, edges)

    # Construct the target instance. Validation of the target will be done by
    # the consumer (the oracle) but we can optionally validate here.
    target = {"n": n, "edges": comp_edges, "k": k}
    # Ensure the produced instance conforms to Clique's format.
    Clique.validate(target)
    return target

