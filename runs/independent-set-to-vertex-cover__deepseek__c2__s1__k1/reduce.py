"""Polynomial-time reduction from Independent Set to Vertex Cover.

For a graph G on n vertices, a set S is an independent set if and only if
its complement V \\ S is a vertex cover.  Therefore G has an independent set
of size at least k exactly when G has a vertex cover of size at most n - k.

So the reduction keeps n and the edge list unchanged and maps k to n - k.
"""


def reduce(instance):
    """Reduce an Independent Set instance to a Vertex Cover instance.

    Input:  {"n": n, "edges": [[u, v], ...], "k": k}
    Output: {"n": n, "edges": [[u, v], ...], "k": n - k}
    """
    n = instance["n"]
    k = instance["k"]
    edges = [list(edge) for edge in instance["edges"]]
    return {"n": n, "edges": edges, "k": n - k}
