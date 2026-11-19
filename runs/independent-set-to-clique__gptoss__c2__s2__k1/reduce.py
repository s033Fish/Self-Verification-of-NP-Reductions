"""Reduction from Independent Set to Clique.

The source problem *Independent Set* asks whether a given undirected graph
contains a set of at least ``k`` vertices with no edges between any two of
them.  The target problem *Clique* asks whether a graph contains a set of at
least ``k`` vertices where every pair is connected by an edge.

It is a classic textbook reduction: an independent set in a graph ``G`` is a
clique in the complement graph ``G̅`` (the graph on the same vertex set where
edges are exactly the non‑edges of ``G``).  Therefore we can transform an
instance of ``IndependentSet`` into an instance of ``Clique`` by constructing
the complement of the input graph while keeping ``n`` and ``k`` unchanged.

The function ``reduce`` below implements this transformation.  It runs in
``O(n^2)`` time – polynomial in the size of the input – and produces an
instance that satisfies the format required by ``problems.py`` for the
``Clique`` problem.
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Independent Set instance to a Clique instance.

    Parameters
    ----------
    instance: dict
        A dictionary representing an Independent Set instance with the keys
        ``"n"`` (number of vertices), ``"edges"`` (list of ``[u, v]`` pairs) and
        ``"k"`` (desired size of the independent set).

    Returns
    -------
    dict
        A dictionary representing a Clique instance that is *yes* exactly when
        the original instance is *yes*.
    """

    n: int = instance["n"]
    k: int = instance["k"]
    # Build a set of existing edges for O(1) look‑ups.  Store as frozenset to be
    # order‑independent.
    edge_set = {frozenset((u, v)) for u, v in instance.get("edges", [])}

    complement_edges: List[List[int]] = []
    # For every unordered pair of distinct vertices, add an edge to the
    # complement if it is *not* present in the original graph.
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in edge_set:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": k}
