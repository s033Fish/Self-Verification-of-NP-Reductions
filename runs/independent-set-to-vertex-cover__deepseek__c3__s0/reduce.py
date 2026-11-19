"""Polynomial-time reduction from Independent Set to Vertex Cover.

Key fact: a set S is a vertex cover of G iff V \\ S is an independent set of G.
Hence G has an independent set of size >= k iff G has a vertex cover of
size <= n - k.

So the reduction keeps the same graph and maps k -> n - k.
"""


def reduce(instance):
    n = instance["n"]
    k = instance["k"]
    return {"n": n, "edges": [list(edge) for edge in instance["edges"]], "k": n - k}
