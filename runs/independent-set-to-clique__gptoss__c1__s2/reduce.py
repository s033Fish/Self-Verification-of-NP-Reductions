"""Reduction from Independent Set to Clique.

Given an instance of Independent Set (graph G and integer k), the reduction
produces an instance of Clique on the complement graph G̅ with the same
parameter k.  An independent set of size k in G corresponds exactly to a
clique of size k in G̅, so the answer is preserved.

The instance format follows the specification in problems.py:
    {"n": n, "edges": [[u, v], ...], "k": k}
where vertices are 0..n-1 and edges are undirected pairs with u != v.
"""

def reduce(instance):
    """Return a Clique instance equivalent to the given Independent Set instance.

    Parameters
    ----------
    instance: dict
        An Independent Set instance with keys "n", "edges", and "k".

    Returns
    -------
    dict
        A Clique instance on the complement graph.
    """
    n = instance["n"]
    k = instance["k"]
    # Build a set of existing edges for O(1) lookup. Store as frozenset({u,v})
    original_edges = set()
    for u, v in instance.get("edges", []):
        # Ensure ordering for consistency
        if u > v:
            u, v = v, u
        original_edges.add((u, v))

    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in original_edges:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": k}

# The module can be imported by the evaluation harness; no top‑level code is executed.
