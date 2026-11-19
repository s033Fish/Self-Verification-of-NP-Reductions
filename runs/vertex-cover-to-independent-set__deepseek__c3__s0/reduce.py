"""Polynomial-time reduction from Vertex Cover to Independent Set.

A set S of vertices is a vertex cover of G iff its complement V \\ S is an
independent set of G.  Therefore G has a vertex cover of size at most k iff
G has an independent set of size at least n - k.

The reduction keeps the graph unchanged and maps the threshold k to n - k.
"""


def reduce(instance):
    n = instance["n"]
    k = instance["k"]
    return {"n": n, "edges": [list(e) for e in instance["edges"]], "k": n - k}
