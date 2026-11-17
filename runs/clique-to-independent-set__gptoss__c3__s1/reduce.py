"""Reduction from Clique to Independent Set.

The source problem is :class:`problems.Clique` and the target problem is
``problems.IndependentSet``.  Both problems use the same graph representation:

    {"n": int, "edges": [[u, v], ...], "k": int}

where ``edges`` is an undirected simple edge list (no duplicates, no self‑loops).

For a graph G, a *clique* of size k exists in G iff an *independent set* of
size k exists in the complement graph \overline{G}.  Therefore the reduction is
simply:

* keep the same number of vertices ``n`` and the same ``k``;
* replace the edge list with the complement edge list.

The implementation below follows this idea.  It validates the source instance
using ``Clique.validate`` (which also checks the ``k`` field) and then builds
the complement edge list in O(n^2) time – polynomial in the size of the input.

The returned instance conforms to the ``IndependentSet`` specification, so it
can be fed directly to ``IndependentSet.is_yes``.
"""

from __future__ import annotations

from typing import List, Dict, Any

import problems


def _complement_edges(n: int, edges: List[List[int]]) -> List[List[int]]:
    """Return the edge list of the complement of a simple undirected graph.

    ``edges`` is assumed to be a valid edge list for a graph on vertices
    ``0..n-1`` (no duplicates, no self‑loops).  The complement contains exactly
    those unordered pairs ``{u, v}`` with ``u < v`` that are *not* present in the
    original edge list.
    """
    # Build a set of frozensets for O(1) membership tests.
    present = {frozenset(edge) for edge in edges}
    complement: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in present:
                complement.append([u, v])
    return complement


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Clique instance to an Independent Set instance.

    Parameters
    ----------
    instance:
        A dictionary representing a Clique instance.  The function first
        validates the instance using ``problems.Clique.validate`` to ensure the
        input adheres to the required format.

    Returns
    -------
    dict
        A dictionary representing an Independent Set instance that is a
        polynomial‑time transformation of the input.
    """
    # Validate the source instance (will raise InvalidInstance on malformed
    # input).  This also guarantees the presence of the "n", "edges", and "k"
    # fields.
    problems.Clique.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Compute the complement edge list.
    comp_edges = _complement_edges(n, edges)

    # Build the target instance.  The format matches IndependentSet.validate.
    reduced_instance: Dict[str, Any] = {"n": n, "edges": comp_edges, "k": k}

    # Validate the target instance as a sanity check (optional but helpful).
    problems.IndependentSet.validate(reduced_instance)
    return reduced_instance

