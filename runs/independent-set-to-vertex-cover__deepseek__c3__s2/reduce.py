"""Polynomial-time reduction from Independent Set to Vertex Cover.

Key fact: a set S is a vertex cover of G iff V \\ S is an independent set
of G.  Hence G has an independent set of size >= k iff G has a vertex
cover of size <= n - k.  The reduction keeps the graph unchanged and maps
the threshold k to n - k.
"""


def reduce(instance):
    """Reduce an Independent Set instance to a Vertex Cover instance.

    Input/output format: {"n": n, "edges": [[u, v], ...], "k": k}
    """
    n = instance["n"]
    k = instance["k"]
    return {"n": n, "edges": [list(edge) for edge in instance["edges"]], "k": n - k}
