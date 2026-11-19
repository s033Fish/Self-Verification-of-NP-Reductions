"""Reduction from Independent Set to Clique.

The source problem (Independent Set) asks whether a given undirected graph
contains an independent set of size at least ``k``.  The target problem (Clique)
asks whether a given undirected graph contains a clique of size at least ``k``.

It is a classic textbook reduction: an independent set in a graph ``G`` is a
clique in the complement graph ``G̅`` (the graph on the same vertex set where
every non‑edge of ``G`` becomes an edge, and vice‑versa).  Therefore we can map
an instance ``(V, E, k)`` of Independent Set to the instance ``(V, E̅, k)`` of
Clique where ``E̅ = { {u, v} | u != v and {u, v} ∉ E }``.

The ``reduce`` function below implements this transformation.  It runs in
polynomial time – specifically ``O(n^2)`` – which is easily within the required
bounds.  Edge cases such as ``k <= 0`` or ``k > n`` are preserved automatically
by keeping ``n`` and ``k`` unchanged.
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Transform an Independent Set instance into a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` representing
        the Independent Set problem as described in ``problems.py``.

    Returns
    -------
    dict
        An instance of the Clique problem with the same ``n`` and ``k`` and
        with edges equal to the complement of the input graph.
    """

    n: int = instance["n"]
    original_edges: List[List[int]] = instance.get("edges", [])
    k: int = instance["k"]

    # Build a set for O(1) membership tests of original edges.
    # Store edges as ordered tuples (min, max) to avoid duplicates.
    edge_set = set()
    for u, v in original_edges:
        if u == v:
            # The problem specification guarantees u != v, but we defensively
            # ignore self‑loops if they appear.
            continue
        a, b = (u, v) if u < v else (v, u)
        edge_set.add((a, b))

    # Construct complement edges.
    complement_edges: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in edge_set:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": k}
