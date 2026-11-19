"""Reduction from Independent Set to Clique.

Given an instance of Independent Set (graph G with n vertices, edge list, and integer k),
produce an instance of Clique on the complement graph G' with the same vertex set and k.
The complement graph has an edge between two distinct vertices iff the original graph does NOT have that edge.
This transformation is polynomial time and preserves yes‑instances:
G has an independent set of size ≥ k ⇔ G' has a clique of size ≥ k.
"""

def reduce(instance):
    """Convert Independent Set instance to Clique instance.

    Parameters
    ----------
    instance : dict
        Dictionary with keys "n", "edges", and "k" representing an Independent Set instance.
        "edges" is a list of [u, v] pairs (undirected, u != v).

    Returns
    -------
    dict
        A Clique instance on the complement graph with the same "n" and "k".
    """
    n = instance["n"]
    k = instance["k"]
    # Build a set of existing edges with ordered tuple (min, max) for quick lookup
    original_edges = set()
    for u, v in instance.get("edges", []):
        if u > v:
            u, v = v, u
        original_edges.add((u, v))

    # Complement edges: all pairs not present in original_edges
    comp_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in original_edges:
                comp_edges.append([u, v])

    return {"n": n, "edges": comp_edges, "k": k}

# The module exports only the reduce function as required by the task.
__all__ = ["reduce"]

