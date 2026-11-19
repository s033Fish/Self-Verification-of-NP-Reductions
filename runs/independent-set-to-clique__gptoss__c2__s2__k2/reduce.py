"""Reduction from Independent Set to Clique.

The source problem is **Independent Set** with instance format:
    {"n": n, "edges": [[u, v], ...], "k": k}
The target problem is **Clique** with the same instance format.

The classic polynomial‑time reduction constructs the complement graph:
    G' = (V, E') where E' contains exactly those unordered pairs of vertices
    that are *not* edges of the original graph G.
An independent set of size ≥ k in G corresponds to a clique of size ≥ k in
the complement G', and vice‑versa.  Edge cases (k ≤ 0, k > n, etc.) are
preserved automatically because the reduction does not change n or k.

The ``reduce`` function below performs this transformation.  It runs in
O(n^2) time, which is polynomial in the size of the input instance.
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Independent Set instance to a Clique instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` describing a
        graph for the Independent Set problem.

    Returns
    -------
    dict
        A dictionary in the same format suitable for the Clique problem.
        The number of vertices ``n`` and the target size ``k`` are unchanged;
        the edge list is the complement of the original edge list.
    """

    n: int = instance["n"]
    original_edges: List[List[int]] = instance.get("edges", [])
    k: int = instance["k"]

    # Build a set for O(1) edge existence checks.  Store as (min, max) tuples
    # because the graph is undirected and edges are unordered.
    edge_set = set()
    for u, v in original_edges:
        if u == v:
            # Self‑loops are irrelevant for Independent Set / Clique definitions,
            # but we ignore them to keep the complement well‑defined.
            continue
        a, b = (u, v) if u < v else (v, u)
        edge_set.add((a, b))

    # Generate complement edges: all unordered pairs not present in edge_set.
    complement_edges: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in edge_set:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": k}
