"""Reduction from Independent Set to Clique.

The source problem (Independent Set) asks whether a given undirected graph
contains an independent set of at least ``k`` vertices.  The target problem
(Clique) asks whether a graph contains a clique of at least ``k`` vertices.

A classic polynomial‑time many‑one reduction is to take the *complement* of
the input graph: a set of vertices is independent in the original graph iff
it forms a clique in the complement.  Therefore we can keep the number of
vertices ``n`` and the parameter ``k`` unchanged and replace the edge list by
the complement edge list.

The instance format for both problems, as described in ``problems.py``, is a
dictionary:

    {"n": int, "edges": [[u, v], ...], "k": int}

where vertices are numbered ``0 .. n-1`` and each edge appears only once
with ``u != v``.

The ``reduce`` function below constructs the complement graph in O(n²) time,
which is polynomial in the size of the input instance.
"""

from typing import List, Dict, Tuple, Set


def _edge_key(u: int, v: int) -> Tuple[int, int]:
    """Return a canonical representation of an undirected edge.

    The input instance guarantees that each edge appears only once and that
    ``u != v``.  By always ordering the vertices we can store edges in a set
    for O(1) membership tests.
    """
    return (u, v) if u < v else (v, u)


def reduce(instance: Dict) -> Dict:
    """Reduce an Independent Set instance to a Clique instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` representing
        the Independent Set instance.

    Returns
    -------
    dict
        A Clique instance with the same ``n`` and ``k`` and with the edge
        list equal to the complement of the original graph.
    """
    n: int = instance["n"]
    original_edges: List[List[int]] = instance.get("edges", [])
    k: int = instance["k"]

    # Store original edges in a set for fast lookup.
    edge_set: Set[Tuple[int, int]] = set()
    for u, v in original_edges:
        edge_set.add(_edge_key(u, v))

    # Build complement edge list.
    complement_edges: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if _edge_key(u, v) not in edge_set:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": k}
