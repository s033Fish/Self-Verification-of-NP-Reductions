"""Reduction from Independent Set to Vertex Cover.

Given an instance of Independent Set with graph (n, edges) and integer k,
produce an instance of Vertex Cover on the same graph with parameter
k' = n - k.  It is well‑known that a set S is independent in G iff its
complement V\S is a vertex cover, so the answers coincide.
"""

def reduce(instance):
    """Convert an Independent Set instance to a Vertex Cover instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys "n", "edges", "k" representing the
        Independent Set problem as described in problems.py.

    Returns
    -------
    dict
        A dictionary representing a Vertex Cover instance with the same
        vertices and edges and with parameter k' = n - k.
    """
    n = instance.get("n")
    edges = instance.get("edges")
    k = instance.get("k")
    # Compute the corresponding vertex‑cover bound.
    k_prime = n - k
    return {"n": n, "edges": edges, "k": k_prime}

# The module can be imported; no top‑level code is executed.
