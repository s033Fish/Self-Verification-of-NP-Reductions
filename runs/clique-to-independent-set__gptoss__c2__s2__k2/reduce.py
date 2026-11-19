"""Reduction from Clique to Independent Set.

The source problem (Clique) asks whether a given undirected graph G = (V,E)
contains a clique of size at least k.  The target problem (IndependentSet)
asks whether a graph contains an independent set of size at least k.

A classic polynomial‑time reduction is to take the complement of the input
graph.  A set of vertices forms a clique in G iff it forms an independent set
in the complement graph G̅ (where every non‑edge of G becomes an edge and vice
versa).  Therefore, the same value of *k* can be used for the target instance.

The ``reduce`` function below implements this transformation.  It receives an
instance dictionary matching the format described in ``problems.py`` for the
Clique problem and returns a new instance dictionary suitable for the
IndependentSet problem.

The implementation runs in O(n²) time, which is polynomial in the size of the
input (n is the number of vertices, and the edge list size is at most n²).
"""

from __future__ import annotations

from typing import List, Dict, Any, Tuple, Set

def _normalize_edge(u: int, v: int) -> Tuple[int, int]:
    """Return a canonical ordered representation of an undirected edge.

    The input edge list may contain each edge only once, but we still store it
    in a set with the smaller vertex first to make membership checks O(1).
    """
    return (u, v) if u < v else (v, u)


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Clique instance to an Independent Set instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` as defined for
        the Clique problem.

    Returns
    -------
    dict
        A new instance dictionary for the IndependentSet problem where the
        graph is the complement of the original graph and ``k`` is unchanged.
    """
    n: int = instance["n"]
    original_edges: List[List[int]] = instance.get("edges", [])
    k: int = instance["k"]

    # Store original edges in a set for O(1) look‑ups.
    edge_set: Set[Tuple[int, int]] = set()
    for u, v in original_edges:
        edge_set.add(_normalize_edge(u, v))

    # Build the complement edge list.
    complement_edges: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in edge_set:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": k}


__all__ = ["reduce"]
