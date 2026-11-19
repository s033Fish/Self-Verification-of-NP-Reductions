"""Reduction from Clique to Vertex Cover.

Given an instance of Clique:
    {"n": n, "edges": [[u, v], ...], "k": k}
we produce an instance of VertexCover on the complement graph with
parameter k' = n - k.

Correctness follows from the standard complement reduction:
A k‑clique in G corresponds to an independent set of size k in the
complement graph G̅, and a vertex cover of size n‑k exists in G̅ iff such
an independent set exists.
"""

def reduce(instance):
    """Reduce a Clique instance to a VertexCover instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys "n", "edges", and "k" describing a graph
        for the Clique problem.

    Returns
    -------
    dict
        A dictionary representing a VertexCover instance on the complement
        graph with parameter n - k.
    """
    n = instance["n"]
    k = instance["k"]
    # Build a set of existing edges (unordered pairs)
    original_edges = set()
    for u, v in instance.get("edges", []):
        if u > v:
            u, v = v, u
        original_edges.add((u, v))
    # Generate complement edges
    comp_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in original_edges:
                comp_edges.append([u, v])
    # New parameter for Vertex Cover
    new_k = n - k
    return {"n": n, "edges": comp_edges, "k": new_k}
