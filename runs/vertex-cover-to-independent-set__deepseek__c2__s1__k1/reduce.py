"""Polynomial-time reduction from Vertex Cover to Independent Set.

Given a Vertex Cover instance G = (V, E) with budget k, the target
Independent Set instance uses the same graph and budget n - k, where
n = |V|.  A set S is independent in G iff V \ S is a vertex cover of G.
Therefore G has an independent set of size at least n - k iff G has a
vertex cover of size at most k.
"""


def reduce(instance):
    """Reduce a Vertex Cover instance to an Independent Set instance."""
    n = instance["n"]
    edges = [list(edge) for edge in instance["edges"]]
    k = instance["k"]
    return {"n": n, "edges": edges, "k": n - k}
