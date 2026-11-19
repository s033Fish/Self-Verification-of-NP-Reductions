"""Polynomial-time reduction from Vertex Cover to Independent Set.

Key fact: a set S of vertices is a vertex cover of G iff its complement
V \\ S is an independent set of G.  Therefore G has a vertex cover of size
AT MOST k iff G has an independent set of size AT LEAST n - k.

So the reduction keeps the graph unchanged and maps k -> n - k.
"""


def reduce(instance):
    """Map a Vertex Cover instance to an Independent Set instance.

    Input : {"n": n, "edges": [[u, v], ...], "k": k}
    Output: {"n": n, "edges": [[u, v], ...], "k": n - k}
    """
    n = instance["n"]
    edges = [list(edge) for edge in instance["edges"]]
    k = instance["k"]
    return {"n": n, "edges": edges, "k": n - k}
