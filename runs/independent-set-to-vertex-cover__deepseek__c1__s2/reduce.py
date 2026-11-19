"""Polynomial-time reduction from Independent Set to Vertex Cover.

Given an Independent Set instance {"n": n, "edges": edges, "k": k},
return the Vertex Cover instance on the same graph with budget k' = n - k.

Correctness: S is an independent set in G iff V \\ S is a vertex cover of G.
Therefore G has an independent set of size >= k iff G has a vertex cover of
size <= n - k.  The construction runs in linear time in the input size.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    return {"n": n, "edges": [list(e) for e in edges], "k": n - k}
