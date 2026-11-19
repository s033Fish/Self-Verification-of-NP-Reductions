"""Reduction from Vertex Cover to Clique.

The source problem (Vertex Cover) is defined as:
    Instance: {"n": n, "edges": [[u, v], ...], "k": k}
    Yes iff there exists a set of at most k vertices that touches every edge.

The target problem (Clique) is defined as:
    Instance: {"n": n, "edges": [[u, v], ...], "k": k}
    Yes iff the graph contains a clique of size at least k.

Standard polynomial‑time reduction:
    Given G = (V, E) and integer k for Vertex Cover, construct the complement
    graph \bar G = (V, \bar E) where (u, v) \in \bar E iff u \neq v and (u, v) \notin E.
    Set k' = n - k.
    Then G has a vertex cover of size ≤ k  ⇔  \bar G has a clique of size ≥ k'.

The function ``reduce`` below implements this transformation.  It runs in
polynomial time (O(n^2)) and correctly handles all edge‑cases described in the
problem specifications.
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Vertex Cover instance to a Clique instance.

    Parameters
    ----------
    instance: dict
        A Vertex Cover instance with keys ``"n"``, ``"edges"`` and ``"k"``.

    Returns
    -------
    dict
        A Clique instance whose answer is *yes* exactly when the input
        Vertex Cover instance's answer is *yes*.
    """
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Build a set for O(1) edge existence checks. Store each edge as a tuple
    # with the smaller vertex first to ensure consistency.
    edge_set = set()
    for u, v in edges:
        if u > v:
            u, v = v, u
        edge_set.add((u, v))

    # Complement edges: all unordered pairs of distinct vertices not present
    # in the original edge set.
    complement_edges: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in edge_set:
                complement_edges.append([u, v])

    # Target k is n - k (size of the clique we need in the complement graph).
    target_k = n - k

    return {"n": n, "edges": complement_edges, "k": target_k}

