"""Reduction from Independent Set to Clique.

The source problem is **Independent Set**:
    Given an undirected graph G = (V, E) and an integer k, does G contain
    an independent set of size at least k?

The target problem is **Clique**:
    Given an undirected graph H = (V, E') and an integer k, does H contain a
    clique of size at least k?

It is well‑known that an independent set in a graph G corresponds to a clique
in the *complement* of G.  The complement graph  G̅  has the same vertex set V
and contains exactly those edges that are **not** present in G (excluding
self‑loops).  Therefore, a set of vertices is independent in G iff it is a
clique in G̅.

The reduction is therefore straightforward:
    1. Read the instance of Independent Set – a dictionary with keys
       ``"n"`` (number of vertices), ``"edges"`` (list of ``[u, v]`` pairs) and
       ``"k"`` (the required size).
    2. Construct the complement edge list by iterating over all unordered
       vertex pairs ``(u, v)`` with ``u < v`` and adding the pair when it is
       **not** present in the original edge set.
    3. Return a new instance dictionary for Clique with the same ``n`` and
       ``k`` but with the complement edge list.

The transformation runs in O(n²) time, which is polynomial in the size of the
input.  It also preserves all edge‑case semantics (k ≤ 0, k > n, empty edge
list, etc.) because the complement of a graph with no edges is the complete
graph and vice‑versa.
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Independent Set instance to a Clique instance.

    Parameters
    ----------
    instance: dict
        A dictionary representing an Independent Set instance with the
        following keys:
        * ``"n"`` – number of vertices (int)
        * ``"edges"`` – list of edges, each edge is a two‑element list
          ``[u, v]`` with ``0 <= u, v < n`` and ``u != v``
        * ``"k"`` – target size (int)

    Returns
    -------
    dict
        A dictionary representing a Clique instance that is equivalent to the
        given Independent Set instance.
    """
    n: int = instance["n"]
    edges: List[List[int]] = instance.get("edges", [])
    k: int = instance["k"]

    # Store original edges in a set for O(1) look‑ups.  Use frozenset to make the
    # pair unordered.
    edge_set = {frozenset((u, v)) for u, v in edges}

    # Build complement edges: all unordered pairs not present in edge_set.
    complement_edges: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in edge_set:
                complement_edges.append([u, v])

    # Return the Clique instance.
    return {"n": n, "edges": complement_edges, "k": k}

