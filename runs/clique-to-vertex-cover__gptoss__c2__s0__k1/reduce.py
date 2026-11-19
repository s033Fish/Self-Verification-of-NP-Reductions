"""Reduction from Clique to Vertex Cover.

The source problem (Clique) asks whether an undirected graph G with n vertices
contains a clique of size at least k.  The target problem (VertexCover) asks
whether G' has a vertex cover of size at most k'.  The classic polynomial‑time
reduction uses the complement graph:

    G has a k‑clique  <=>  the complement of G has a vertex cover of size n‑k.

Explanation:
* A set C of vertices forms a clique in G iff every *non‑edge* of G has at
  least one endpoint outside C.  Equivalently, the complement graph G̅ has the
  property that the vertices V\C (the complement of C) touch every edge of
  G̅, i.e., V\C is a vertex cover of G̅.
* Therefore, a clique of size k corresponds to a vertex cover of size n‑k in
  the complement.

The reduction is straightforward:
1. Compute the complement edge set of the input graph.
2. Keep the same number of vertices n.
3. Set the new parameter k' = n - k.

Edge‑case handling follows automatically from the definition:
* If k <= 0, the source is a yes‑instance; then k' >= n, and VertexCover is a
  yes‑instance because k' >= n is always yes.
* If k > n, the source is a no‑instance; then k' < 0, and VertexCover is a no‑
  instance because k' < 0 is always no.

The implementation runs in O(n^2) time, which is polynomial in the size of
the input.
"""

from __future__ import annotations

from typing import Dict, List, Tuple, Set


def reduce(instance: Dict) -> Dict:
    """Reduce a Clique instance to a VertexCover instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` representing a
        Clique instance as described in ``problems.py``.

    Returns
    -------
    dict
        A VertexCover instance with the same ``n`` and the complement edge set.
        The new ``k`` value is ``n - k``.
    """

    n: int = instance["n"]
    k: int = instance["k"]
    edges: List[List[int]] = instance.get("edges", [])

    # Store existing edges as a set of unordered pairs for O(1) look‑ups.
    existing: Set[Tuple[int, int]] = set()
    for u, v in edges:
        if u > v:
            u, v = v, u
        existing.add((u, v))

    # Build complement edges: all pairs (i, j) with i < j that are not in existing.
    complement_edges: List[List[int]] = []
    for i in range(n):
        for j in range(i + 1, n):
            if (i, j) not in existing:
                complement_edges.append([i, j])

    # New k value for VertexCover.
    new_k = n - k

    return {"n": n, "edges": complement_edges, "k": new_k}

