"""Polynomial-time reduction from Independent Set to Vertex Cover.

An instance of Independent Set is a graph G = (V, E) together with an
integer k; it is a yes-instance iff G has an independent set of size at
least k.

Key fact: a set S is an independent set in G iff its complement V \\ S is
a vertex cover of G.  Therefore G has an independent set of size at least
k iff G has a vertex cover of size at most n - k.

So the reduction keeps the graph unchanged and maps k -> n - k.

This also respects the edge cases:
  * k <= 0 (source always yes)  -> n - k >= n (target always yes).
  * k > n  (source always no)   -> n - k < 0 (target always no).
"""


def reduce(instance):
    """Map an Independent Set instance to a Vertex Cover instance."""
    n = instance["n"]
    edges = [list(edge) for edge in instance["edges"]]
    k = instance["k"]
    return {"n": n, "edges": edges, "k": n - k}
