"""Reduction from Clique to Vertex Cover.

Given a Clique instance (n, edges, k), we construct a VertexCover instance
on the complement graph with parameter k' = n - k.  It is well‑known that
G has a clique of size at least k iff the complement graph \bar G has an
independent set of size at least k, which is equivalent to a vertex cover of
size at most n‑k.

The reduction runs in O(n^2) time, which is polynomial.
"""

def reduce(instance):
    """Transform a Clique instance into a VertexCover instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys "n", "edges", and "k" describing a graph for
        the Clique problem.

    Returns
    -------
    dict
        A dictionary suitable for the VertexCover problem.
    """
    n = instance["n"]
    k = instance["k"]
    # Build a set of existing edges for O(1) lookup. Store each edge as a tuple (u, v) with u < v.
    edge_set = set()
    for u, v in instance.get("edges", []):
        if u > v:
            u, v = v, u
        edge_set.add((u, v))
    # Complement edges: all unordered pairs not present in edge_set.
    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in edge_set:
                complement_edges.append([u, v])
    # New parameter for VertexCover.
    new_k = n - k
    return {"n": n, "edges": complement_edges, "k": new_k}

# The module may be imported by the evaluation harness; expose the function.
__all__ = ["reduce"]
