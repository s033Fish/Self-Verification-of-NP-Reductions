"""Polynomial-time reduction from Independent Set to Vertex Cover.

For a graph G with n vertices, a set S is an independent set if and only if
its complement V \\ S is a vertex cover.  Therefore G has an independent set
of size at least k exactly when G has a vertex cover of size at most n - k.

The reduction keeps the same graph and maps the parameter k to n - k.
"""


def reduce(instance):
    """Reduce an Independent Set instance to an equivalent Vertex Cover instance."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    return {
        "n": n,
        "edges": [list(edge) for edge in edges],
        "k": n - k,
    }
