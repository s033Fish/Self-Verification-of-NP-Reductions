"""Polynomial-time reduction from Vertex Cover to Independent Set.

Given a Vertex Cover instance (G, k), produce the Independent Set instance
(G, n - k).  A set C is a vertex cover of G if and only if V \\ C is an
independent set of G.  Hence G has a vertex cover of size at most k exactly
when G has an independent set of size at least n - k.

The reduction leaves n and edges unchanged and runs in O(n + m) time.
"""


def reduce(instance):
    """Reduce a Vertex Cover instance to an Independent Set instance."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Copy the edge list so the returned instance does not alias the input.
    target_edges = [[u, v] for (u, v) in edges]

    return {"n": n, "edges": target_edges, "k": n - k}
