"""Reduction from Clique to Vertex Cover.

The classic polynomial‑time many‑one reduction works via the graph
complement.  A set of vertices forms a clique of size *k* in a graph *G*
iff the complementary set of vertices is a vertex cover of size *n‑k*
in the complement graph \bar{G}.

Given an instance of the *Clique* problem:

    {"n": n, "edges": [[u, v], ...], "k": k}

we construct a *VertexCover* instance with the same number of vertices,
the edge set being the complement of the original edge set, and the new
parameter ``k' = n - k``.

This transformation preserves the answer for all edge cases (e.g. ``k``
non‑positive or larger than ``n``) and runs in polynomial time – in fact
quadratic in ``n`` which is easily within the required bounds.
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Clique instance to a VertexCover instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` representing
        the Clique problem as described in ``problems.py``.

    Returns
    -------
    dict
        An instance of the VertexCover problem with the same ``n`` and
        ``edges`` equal to the complement of the input graph's edges, and
        ``k`` set to ``n - original_k``.
    """

    n: int = instance["n"]
    original_edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Build a set for O(1) edge existence checks. Store each edge as a
    # tuple with the smaller vertex first to avoid duplication.
    edge_set = set()
    for u, v in original_edges:
        if u > v:
            u, v = v, u
        edge_set.add((u, v))

    # Generate complement edges: all unordered pairs (i, j) with i < j
    # that are not present in the original edge set.
    complement_edges: List[List[int]] = []
    for i in range(n):
        for j in range(i + 1, n):
            if (i, j) not in edge_set:
                complement_edges.append([i, j])

    # The new k for VertexCover is n - k (size of the complement of a
    # potential clique).
    new_k = n - k

    return {"n": n, "edges": complement_edges, "k": new_k}

