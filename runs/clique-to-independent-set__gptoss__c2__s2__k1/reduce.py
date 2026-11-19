"""Reduction from Clique to Independent Set.

The source problem (Clique) and the target problem (IndependentSet) share the
same instance format: a dictionary with keys ``n`` (number of vertices),
``edges`` (list of undirected edges as ``[u, v]``) and ``k`` (the size bound).

For a graph G = (V, E) the complement graph G̅ = (V, \overline{E}) contains an
edge between two distinct vertices iff the original graph does **not** contain
that edge.  A set of vertices forms a clique in G exactly when it forms an
independent set in G̅.  Therefore, to reduce an instance of Clique to an
instance of Independent Set we keep ``n`` and ``k`` unchanged and replace the
edge list with the complement edge list.

The reduction runs in O(n²) time, which is polynomial in the size of the input
instance.
"""

from __future__ import annotations

from typing import Dict, List

# The type used by the problem definitions – a plain dictionary.
Instance = Dict[str, object]


def _complement_edges(n: int, edges: List[List[int]]) -> List[List[int]]:
    """Return the edge list of the complement graph.

    ``edges`` is assumed to be a valid edge list for a simple undirected graph
    on ``n`` vertices (no self‑loops, no duplicate edges, each edge appears as
    ``[u, v]`` with ``u != v``).  The result contains each unordered pair
    ``{u, v}`` exactly once where ``u < v`` and the pair is *not* present in the
    original edge list.
    """
    # Store original edges in a set of frozensets for O(1) membership tests.
    existing = {frozenset((u, v)) for u, v in edges}
    complement: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in existing:
                complement.append([u, v])
    return complement


def reduce(instance: Instance) -> Instance:
    """Reduce a Clique instance to an IndependentSet instance.

    The function assumes ``instance`` is a valid Clique instance (the caller
    may have validated it using ``Clique.validate``).  It returns a new
    dictionary that conforms to the IndependentSet specification:

    * ``n`` – unchanged.
    * ``edges`` – the complement of the original edge list.
    * ``k`` – unchanged.

    The reduction preserves the answer: the original graph has a clique of
    size at least ``k`` iff the complement graph has an independent set of size
    at least ``k``.
    """
    n = instance["n"]  # type: ignore[index]
    edges = instance["edges"]  # type: ignore[index]
    k = instance["k"]  # type: ignore[index]

    # Compute complement edges.
    comp_edges = _complement_edges(n, edges)  # type: ignore[arg-type]

    # Construct the target instance.
    return {"n": n, "edges": comp_edges, "k": k}

