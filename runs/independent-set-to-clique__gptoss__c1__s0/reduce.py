"""Reduction from Independent Set to Clique.

The source problem (Independent Set) asks whether a given undirected graph
``G = (V, E)`` contains an independent set of size at least ``k`` – a set of
vertices with **no** edges between any two of them.

The target problem (Clique) asks whether a graph contains a clique of size at
least ``k`` – a set of vertices where **every** pair is connected by an edge.

It is a classic textbook reduction: an independent set in a graph ``G`` is a
clique in the *complement* graph ``\overline{G}``.  The complement graph has the
same vertex set and contains exactly those edges that are **not** present in
``G`` (excluding self‑loops).

Given an instance of the source problem, we construct an instance of the
target problem with:

* ``n`` – unchanged.
* ``k`` – unchanged.
* ``edges`` – the edge set of the complement graph.

The construction runs in ``O(n^2)`` time, which is polynomial in the size of
the input.  The resulting instance satisfies the format required by
``problems.py``: vertices are numbered ``0..n-1`` and each undirected edge is
represented exactly once with ``[u, v]`` where ``u < v``.
"""

from typing import List, Dict, Any


def _canonical_edge(u: int, v: int) -> List[int]:
    """Return an edge list ``[u, v]`` with ``u < v``.

    The input instance guarantees ``u != v`` but does not guarantee ordering.
    Normalising the order makes it easy to avoid duplicate edges.
    """
    return [u, v] if u < v else [v, u]


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Independent Set instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` describing an
        independent‑set problem as documented in ``problems.py``.

    Returns
    -------
    dict
        A new instance dictionary for the Clique problem.  The answer to the
        Clique instance is *yes* iff the answer to the original Independent
        Set instance is *yes*.
    """
    n: int = instance["n"]
    k: int = instance["k"]
    original_edges = instance.get("edges", [])

    # Store original edges in a set of tuples (u, v) with u < v for O(1)
    # membership checks.
    edge_set = set()
    for u, v in original_edges:
        if u == v:
            # Self‑loops are not allowed by the problem definition, but we
            # simply ignore them if they appear.
            continue
        edge_set.add(tuple(_canonical_edge(u, v)))

    # Generate complement edges: all unordered pairs (i, j) with i < j that are
    # not present in the original edge set.
    complement_edges: List[List[int]] = []
    for i in range(n):
        for j in range(i + 1, n):
            if (i, j) not in edge_set:
                complement_edges.append([i, j])

    # Construct the target instance.
    return {
        "n": n,
        "k": k,
        "edges": complement_edges,
    }

