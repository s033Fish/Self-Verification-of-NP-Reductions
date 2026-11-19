"""Polynomial-time reduction from Independent Set to Vertex Cover.

For a graph G on n vertices, a set S is independent in G if and only if
its complement V \ S is a vertex cover of G.  Consequently G has an
independent set of size at least k exactly when G has a vertex cover of
size at most n - k.

The reduction therefore keeps the graph unchanged and maps the threshold
k to n - k.  It runs in O(len(edges)) time and never solves either
problem.
"""


def reduce(instance):
    """Map an Independent Set instance to a Vertex Cover instance.

    Input:  {"n": n, "edges": [[u, v], ...], "k": k}
    Output: {"n": n, "edges": [[u, v], ...], "k": n - k}
    """
    n = instance["n"]
    k = instance["k"]
    # Copy the edge list so the returned instance shares no mutable state
    # with the input (edges themselves are immutable pairs).
    edges = [list(edge) for edge in instance["edges"]]
    return {"n": n, "edges": edges, "k": n - k}
