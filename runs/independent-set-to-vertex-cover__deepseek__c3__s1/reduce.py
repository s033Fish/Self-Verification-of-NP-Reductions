"""Polynomial-time reduction from Independent Set to Vertex Cover.

An independent set S is exactly the complement of a vertex cover: S is
independent iff every edge has at least one endpoint outside S, i.e. V \\ S
is a vertex cover.  Hence G has an independent set of size >= k iff G has a
vertex cover of size <= n - k.

So the reduction keeps n and edges and maps k -> n - k.
"""


def reduce(instance):
    n = instance["n"]
    edges = [list(e) for e in instance["edges"]]
    k = instance["k"]
    return {"n": n, "edges": edges, "k": n - k}
