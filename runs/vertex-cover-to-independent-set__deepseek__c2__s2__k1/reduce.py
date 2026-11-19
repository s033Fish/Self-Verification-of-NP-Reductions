"""Polynomial-time reduction from Vertex Cover to Independent Set.

A set S of vertices is a vertex cover of a graph G exactly when its
complement V \\ S is an independent set of G.  Therefore G has a vertex
cover of size at most k if and only if G has an independent set of size at
least n - k, where n is the number of vertices.

The reduction keeps the graph unchanged and maps the threshold k to n - k.
It runs in O(n + m) time (linear in the instance encoding), so it is a
polynomial-time many-one reduction.
"""


def reduce(instance):
    """Reduce a Vertex Cover instance to an Independent Set instance.

    Input:  {"n": n, "edges": [[u, v], ...], "k": k}   (Vertex Cover)
    Output: {"n": n, "edges": [[u, v], ...], "k": n-k} (Independent Set)
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Copy the edge list so the returned instance shares no mutable state
    # with the input instance.
    return {
        "n": n,
        "edges": [list(edge) for edge in edges],
        "k": n - k,
    }
