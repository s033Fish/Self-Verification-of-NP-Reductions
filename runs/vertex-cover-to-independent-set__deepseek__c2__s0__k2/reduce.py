"""Polynomial-time reduction from Vertex Cover to Independent Set.

A set S of vertices is a vertex cover of G = (V, E) if and only if its
complement V \\ S is an independent set: an edge has both endpoints outside S
exactly when neither endpoint is in S, i.e. when that edge lies entirely
inside V \\ S.  Consequently G has a vertex cover of size at most k iff G has
an independent set of size at least n - k.

The reduction therefore keeps the graph unchanged and maps the budget k to
n - k.  This also handles the documented edge cases:

  * k < 0:            source is no; target k' = n - k > n is no.
  * no edges, k >= 0: source is yes; target k' = n - k <= n is yes.
  * k >= n:           source is yes; target k' = n - k <= 0 is yes.
"""


def reduce(instance):
    """Reduce a Vertex Cover instance to an Independent Set instance.

    Input:  {"n": n, "edges": [[u, v], ...], "k": k}
    Output: {"n": n, "edges": [[u, v], ...], "k": n - k}
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Copy the edge list so the returned instance does not alias the input.
    return {
        "n": n,
        "edges": [[u, v] for u, v in edges],
        "k": n - k,
    }
