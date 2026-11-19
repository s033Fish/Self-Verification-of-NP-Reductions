"""Polynomial-time reduction from Vertex Cover to Independent Set.

A set S is a vertex cover of graph G iff V \\ S is an independent set of G.
Therefore G has a vertex cover of size at most k iff G has an independent set
of size at least n - k, where n = |V|.  The reduction keeps the graph
unchanged and maps the parameter k to n - k.
"""


def reduce(instance):
    """Reduce a Vertex Cover instance to an Independent Set instance.

    Input:  {"n": n, "edges": [[u, v], ...], "k": k}
    Output: {"n": n, "edges": [[u, v], ...], "k": n - k}
    """
    n = instance["n"]
    k = instance["k"]
    return {"n": n, "edges": instance["edges"], "k": n - k}
