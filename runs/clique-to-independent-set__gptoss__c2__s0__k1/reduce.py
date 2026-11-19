"""Reduction from Clique to Independent Set.

The source problem is *Clique* defined with the instance format:
    {"n": n, "edges": [[u, v], ...], "k": k}
where vertices are 0..n-1 and edges are undirected.

The target problem is *IndependentSet* with the same instance format.

Standard polynomial‑time reduction: given a graph G, construct its complement
graph \overline{G}.  A set of vertices forms a clique in G iff it forms an
independent set in \overline{G}.  The parameter k remains unchanged.

The function ``reduce`` below performs this transformation.  It runs in
O(n^2) time, which is polynomial in the size of the input instance.
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Clique instance to an Independent Set instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` following the
        specification of the Clique problem.

    Returns
    -------
    dict
        An instance of the Independent Set problem that is a yes‑instance
        exactly when the input is a yes‑instance.
    """

    n: int = instance["n"]
    k: int = instance["k"]
    # Build a set for quick lookup of existing edges.
    # Store each undirected edge as a frozenset of its two vertices.
    edge_set = {frozenset(edge) for edge in instance.get("edges", [])}

    complement_edges: List[List[int]] = []
    # Iterate over all unordered pairs of distinct vertices.
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in edge_set:
                # (u, v) is not an edge in G, so it becomes an edge in the complement.
                complement_edges.append([u, v])

    # The target instance uses the same n and k.
    return {"n": n, "edges": complement_edges, "k": k}

