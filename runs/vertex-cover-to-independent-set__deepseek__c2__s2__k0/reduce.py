"""Polynomial-time reduction from Vertex Cover to Independent Set.

Given a Vertex Cover instance {"n": n, "edges": edges, "k": k}, return the
Independent Set instance {"n": n, "edges": edges, "k": n - k}.

Correctness: a set S of vertices is a vertex cover of G iff its complement
V \ S is an independent set of G.  Therefore G has a vertex cover of size at
most k iff G has an independent set of size at least n - k.

Edge cases:
  * k < 0: the source is no; the target threshold n - k > n, so the target is
    no as well.
  * k >= n: the source is yes (all vertices cover every edge); the target
    threshold n - k <= 0, so the target is yes as well.

The reduction only copies the graph and performs one subtraction, so it runs
in polynomial time (linear in the size of the input).
"""


def reduce(instance):
    """Reduce a Vertex Cover instance to an Independent Set instance."""
    n = instance["n"]
    k = instance["k"]
    edges = [list(edge) for edge in instance["edges"]]
    return {"n": n, "edges": edges, "k": n - k}
