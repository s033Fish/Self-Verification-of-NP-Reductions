"""Polynomial-time reduction from Vertex Cover to Independent Set.

A set S of vertices is a vertex cover of G iff its complement V \\ S is an
independent set of G.  Therefore G has a vertex cover of size AT MOST k iff G
has an independent set of size AT LEAST n - k.  The reduction keeps the graph
unchanged and maps k to n - k.
"""


def reduce(instance):
    n = instance["n"]
    edges = [list(edge) for edge in instance["edges"]]
    k = instance["k"]
    return {"n": n, "edges": edges, "k": n - k}
