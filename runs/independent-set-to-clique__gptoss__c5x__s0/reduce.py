"""Reduction from Independent Set to Clique.

The classic polynomial‑time reduction transforms a graph G into its
complement \bar{G}.  An independent set of size k in G is exactly a clique of
size k in \bar{G}.  The vertex set is unchanged, only the edge set is
complemented (excluding self‑loops).

Both the source and target problems use the same instance format:

    {"n": n, "edges": [[u, v], ...], "k": k}

where vertices are 0..n‑1 and edges are undirected pairs with u != v.  The
reduction therefore returns a dictionary with the same keys, where the edge
list contains every unordered pair of distinct vertices that is *not* an
edge of the original instance.

The function runs in O(n^2) time, which is polynomial in the size of the
input.
"""

from __future__ import annotations

from typing import List, Dict, Any


def _edge_set(edges: List[List[int]]) -> set[frozenset[int]]:
    """Convert the list representation of edges to a set of frozensets.

    The input follows the validation rules of :class:`IndependentSet`, i.e.
    each edge is a list ``[u, v]`` with ``u != v``.  The function does not
    perform validation itself – the caller should have validated the
    instance beforehand.
    """

    return {frozenset(edge) for edge in edges}


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Independent Set instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary representing an Independent Set instance as defined in
        ``problems.py``.

    Returns
    -------
    dict
        A Clique instance with the same ``n`` and ``k`` and with the edge set
        complemented.
    """

    # Extract fields – we trust the caller (the testing harness) to have
    # validated the instance using ``IndependentSet.validate``.
    n: int = instance["n"]
    original_edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Build a set for O(1) membership checks.
    original_edge_set = _edge_set(original_edges)

    # Generate complement edges: all unordered pairs (i, j) with i < j that are
    # not present in the original graph.
    complement_edges: List[List[int]] = []
    for i in range(n):
        for j in range(i + 1, n):
            if frozenset((i, j)) not in original_edge_set:
                complement_edges.append([i, j])

    return {"n": n, "edges": complement_edges, "k": k}

