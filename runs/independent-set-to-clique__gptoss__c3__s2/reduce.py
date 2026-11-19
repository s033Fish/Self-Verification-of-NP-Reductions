"""Reduction from Independent Set to Clique.

The source problem is :class:`problems.IndependentSet` and the target is
``problems.Clique``.  Both problems use the same graph representation – a
dictionary with keys ``"n"`` (number of vertices), ``"edges"`` (list of
undirected edges) and ``"k"`` (size parameter).  An *independent set* of size
``k`` in a graph ``G`` is exactly a *clique* of size ``k`` in the complement
graph ``\overline G``.

The reduction therefore constructs the complement of the input graph and
returns an instance of ``Clique`` with the same ``k``.  The construction is
polynomial in ``n`` (quadratic time) and respects the required instance
format – no self‑loops, no duplicate edges, and vertices are numbered
``0..n-1``.

The function validates the source instance using ``IndependentSet.validate``
so that malformed inputs raise ``InvalidInstance`` just as the original
problem would.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import IndependentSet, Clique, InvalidInstance


def _complement_edges(n: int, edges: List[List[int]]) -> List[List[int]]:
    """Return the edge list of the complement graph.

    ``edges`` is assumed to be a valid list of undirected edges of a simple
    graph on vertices ``0..n-1`` (no self‑loops, no duplicates).  The complement
    contains exactly those unordered pairs ``{u, v}`` with ``u != v`` that are
    *not* present in ``edges``.
    """
    # Store existing edges as frozensets for O(1) membership tests.
    existing = {frozenset((u, v)) for u, v in edges}
    comp: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in existing:
                comp.append([u, v])
    return comp


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Independent Set instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary representing an Independent Set instance as described in
        ``problems.IndependentSet``.

    Returns
    -------
    dict
        A Clique instance that is a yes‑instance iff the original instance is
        a yes‑instance.
    """
    # Validate the source instance; this will raise InvalidInstance on bad
    # input, matching the behaviour expected by the benchmark harness.
    IndependentSet.validate(instance)

    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Build the complement graph.
    comp_edges = _complement_edges(n, edges)

    # The target instance follows the same schema as Clique expects.
    return {"n": n, "edges": comp_edges, "k": k}

