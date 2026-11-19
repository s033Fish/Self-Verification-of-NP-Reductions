"""Polynomial-time reduction from Vertex Cover to Independent Set.

A set S is a vertex cover of G = (V, E) iff V \ S is an independent set.
Therefore G has a vertex cover of size at most k iff G has an independent
set of size at least n - k.

The reduction keeps the graph unchanged and maps the budget k to n - k.
"""


def reduce(instance):
    """Reduce a VertexCover instance to an IndependentSet instance.

    Source instance format:
        {"n": n, "edges": [[u, v], ...], "k": k}
    Target instance format:
        {"n": n, "edges": [[u, v], ...], "k": k}
    """
    n = instance["n"]
    edges = [list(edge) for edge in instance["edges"]]
    k = instance["k"]

    return {
        "n": n,
        "edges": edges,
        "k": n - k,
    }
