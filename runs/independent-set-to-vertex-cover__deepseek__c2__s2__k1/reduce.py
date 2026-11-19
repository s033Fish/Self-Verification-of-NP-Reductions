"""Polynomial-time reduction from Independent Set to Vertex Cover.

For a graph G = (V, E), a set S is an independent set if and only if its
complement V \ S is a vertex cover.  Indeed, S has no edge inside it iff
every edge has at least one endpoint outside S, i.e. in V \ S.

Therefore G has an independent set of size at least k iff G has a vertex
cover of size at most n - k.  The reduction keeps the same graph and maps
k to n - k.
"""


def reduce(instance):
    n = instance["n"]
    edges = [[u, v] for u, v in instance["edges"]]
    k = instance["k"]
    return {"n": n, "edges": edges, "k": n - k}
