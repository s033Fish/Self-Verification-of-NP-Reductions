"""Reduction from Clique to Independent Set.

The source problem is **Clique** with instance format:
    {"n": n, "edges": [[u, v], ...], "k": k}
The target problem is **IndependentSet** with the same format.

The classic polynomial‑time reduction constructs the complement graph:
    G' = (V, E') where (u, v) ∈ E' ⇔ (u, v) ∉ E and u ≠ v.
A set of vertices forms a clique of size ≥ k in G iff it forms an
independent set of size ≥ k in the complement graph G'.

The ``reduce`` function below implements this transformation.  It
preserves the number of vertices ``n`` and the parameter ``k`` and
produces the list of edges of the complement graph.  The implementation
runs in O(n²) time, which is polynomial in the input size.
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Clique instance to an Independent Set instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys ``"n"`` (int), ``"edges"`` (list of [u, v]),
        and ``"k"`` (int) describing a graph for the Clique problem.

    Returns
    -------
    dict
        A dictionary in the format required by the Independent Set
        problem representing the complement graph of the input.
    """

    n: int = instance["n"]
    original_edges: List[List[int]] = instance.get("edges", [])
    k: int = instance["k"]

    # Store existing edges in a set for O(1) look‑ups.  Since the graph is
    # undirected we store each edge with the smaller vertex first.
    edge_set = set()
    for u, v in original_edges:
        if u == v:
            # Self‑loops are not allowed by the problem definition, but we
            # ignore them defensively.
            continue
        a, b = (u, v) if u < v else (v, u)
        edge_set.add((a, b))

    # Build the complement edge list.
    complement_edges: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in edge_set:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": k}

