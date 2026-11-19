"""Reduction from Clique to Independent Set.

The source problem (Clique) and the target problem (IndependentSet) are
defined in ``problems.py``.  Both use the same instance format:

    {"n": int, "edges": [[u, v], ...], "k": int}

Vertices are numbered 0..n-1 and ``edges`` contains each undirected edge
exactly once (i.e., ``[u, v]`` and ``[v, u]`` are considered the same edge).

The classic polynomial‑time reduction builds the complement graph: a set of
vertices forms a clique in the original graph iff it forms an independent set
in the complement.  Therefore we keep ``n`` and ``k`` unchanged and replace the
edge list with the complement of the original edge set.

The ``reduce`` function below performs this transformation.  It runs in
``O(n^2)`` time, which is polynomial in the size of the input instance.
"""

from typing import List, Dict, Any


def _edge_key(u: int, v: int) -> tuple:
    """Return a canonical representation of an undirected edge.

    The input edges may be given in any order, but the reduction treats ``[u,
    v]`` and ``[v, u]`` as the same edge.  By sorting the vertices we obtain a
    unique key that can be stored in a set for fast membership tests.
    """
    return (u, v) if u < v else (v, u)


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Clique instance to an Independent Set instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` representing a
        Clique problem instance.

    Returns
    -------
    dict
        An Independent Set instance that is a yes‑instance exactly when the
        original Clique instance is a yes‑instance.
    """
    n: int = instance["n"]
    k: int = instance["k"]
    original_edges: List[List[int]] = instance.get("edges", [])

    # Build a set of existing edges for O(1) look‑ups.
    edge_set = set(_edge_key(u, v) for u, v in original_edges)

    # Generate the complement edge list.
    complement_edges: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if _edge_key(u, v) not in edge_set:
                complement_edges.append([u, v])

    # The target instance has the same number of vertices and the same k.
    return {"n": n, "edges": complement_edges, "k": k}

