"""Reduction from Clique to Vertex Cover.

The source problem *Clique* asks whether an undirected graph G = (V, E) has a
clique of size at least ``k``.  The target problem *VertexCover* asks whether the
same graph (or any graph) has a vertex cover of size at most ``k``.

Standard polynomial‑time reduction:
    Given an instance (G, k) of Clique, construct the *complement* graph \bar G
    on the same vertex set V.  In \bar G we place an edge between two distinct
    vertices iff that edge is **not** present in G.  Then set
    ``k' = |V| - k``.

It is well‑known that G contains a clique of size ≥ k iff \bar G contains a
vertex cover of size ≤ |V|‑k.  The proof is immediate: the vertices outside a
clique cover all non‑edges, i.e., all edges of the complement graph, and vice
versa.

The reduction runs in O(n²) time, which is polynomial in the size of the input
instance.

The function ``reduce`` below follows the exact instance format described in
``problems.py`` for both problems.  It does **not** invoke any solver; it merely
transforms the data structure.
"""

from typing import List, Dict, Any


def _edge_key(u: int, v: int) -> tuple:
    """Return a canonical (ordered) representation of an undirected edge.

    The input instance guarantees ``u != v`` and that each unordered pair appears
    at most once, but the order may be arbitrary.  By sorting we can store edges
    in a set for O(1) lookup.
    """
    return (u, v) if u < v else (v, u)


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Clique instance to a VertexCover instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` representing a
        Clique instance as documented in ``problems.py``.

    Returns
    -------
    dict
        A VertexCover instance with the same ``n`` and the complement edge set.
        The new ``k`` is ``n - original_k``.
    """
    n: int = instance["n"]
    original_edges: List[List[int]] = instance.get("edges", [])
    k: int = instance["k"]

    # Build a set of existing edges for O(1) membership tests.
    edge_set = { _edge_key(u, v) for u, v in original_edges }

    # Generate complement edges: all unordered pairs {u, v} with u < v that are
    # not present in the original graph.
    complement_edges: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if _edge_key(u, v) not in edge_set:
                complement_edges.append([u, v])

    # New k for VertexCover instance.
    new_k = n - k

    return {"n": n, "edges": complement_edges, "k": new_k}

