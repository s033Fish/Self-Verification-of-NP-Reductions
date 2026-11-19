"""Reduction from Clique to Vertex Cover.

The source problem (Clique) is defined as:
    Instance: {"n": n, "edges": [[u, v], ...], "k": k}
    Yes iff the graph contains a clique of size at least ``k``.

The target problem (VertexCover) is defined as:
    Instance: {"n": n, "edges": [[u, v], ...], "k": k}
    Yes iff the graph has a vertex cover of size at most ``k``.

Standard polynomial‑time reduction:
    * Given a graph G = (V, E) and integer k for Clique, construct the
      complement graph \overline{G} = (V, \overline{E}) where an edge exists
      between two distinct vertices iff it is **not** present in E.
    * Set k' = |V| - k.
    * Then G has a clique of size ≥ k ⇔ \overline{G} has a vertex cover of
      size ≤ k'.

The reduction also correctly handles the edge cases described in the
doc‑strings of the two problems:
    - k ≤ 0  → k' ≥ n, and VertexCover is trivially yes because k' ≥ n.
    - k = 1  → k' = n‑1, and any graph has a vertex cover of size n‑1.
    - k > n  → k' < 0, and VertexCover is trivially no because k' < 0.

The ``reduce`` function below performs this transformation in O(n²) time,
which is polynomial in the size of the input instance.
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Clique instance to an equivalent VertexCover instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` representing
        the Clique problem instance.

    Returns
    -------
    dict
        A dictionary representing the corresponding VertexCover instance.
    """
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Build a set of existing edges for O(1) look‑up. Store each edge as a
    # tuple (min(u, v), max(u, v)) to treat (u, v) and (v, u) as identical.
    existing = set()
    for u, v in edges:
        if u == v:
            # The problem statement guarantees u != v, but we guard against
            # malformed input just in case.
            continue
        a, b = (u, v) if u < v else (v, u)
        existing.add((a, b))

    # Complement edges: all unordered pairs of distinct vertices not in
    # ``existing``.
    complement_edges: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in existing:
                complement_edges.append([u, v])

    # The new k for VertexCover.
    k_prime = n - k

    return {"n": n, "edges": complement_edges, "k": k_prime}


__all__ = ["reduce"]
