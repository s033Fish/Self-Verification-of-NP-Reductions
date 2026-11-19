"""Reduction from Independent Set to Clique.

The source problem (Independent Set) asks whether a given undirected graph
contains a set of at least ``k`` vertices with no edges between any two of them.
The target problem (Clique) asks whether a graph contains a set of at least
``k`` vertices where every pair is connected by an edge.

It is classic that an independent set in a graph ``G`` corresponds to a clique
in the complement graph ``\\overline{G}``.  The complement graph has the same
vertex set, and an edge ``{u, v}`` exists in the complement iff it does **not**
exist in the original graph (and ``u != v``).

The reduction therefore:
    * keeps the number of vertices ``n`` unchanged,
    * keeps the parameter ``k`` unchanged, and
    * replaces the edge list by the complement edge list.

The transformation runs in ``O(n^2)`` time, which is polynomial in the size of
the input instance.
"""

from typing import List, Dict, Any


def _complement_edges(n: int, edges: List[List[int]]) -> List[List[int]]:
    """Return the list of edges of the complement graph.

    The input ``edges`` is assumed to be a list of undirected edges where each
    edge appears exactly once (i.e., ``[u, v]`` and ``[v, u]`` are not both
    present).  The returned list follows the same convention.
    """
    # Store existing edges as ordered tuples (min, max) for O(1) lookup.
    existing = set()
    for u, v in edges:
        if u > v:
            u, v = v, u
        existing.add((u, v))

    complement: List[List[int]] = []
    for i in range(n):
        for j in range(i + 1, n):
            if (i, j) not in existing:
                complement.append([i, j])
    return complement


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Independent Set instance to a Clique instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` following the
        format described in ``problems.py`` for the Independent Set problem.

    Returns
    -------
    dict
        An instance of the Clique problem that is a yes‑instance iff the
        original instance is a yes‑instance.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Compute complement edges.
    comp_edges = _complement_edges(n, edges)

    # The target instance uses the same ``n`` and ``k``.
    return {"n": n, "edges": comp_edges, "k": k}

