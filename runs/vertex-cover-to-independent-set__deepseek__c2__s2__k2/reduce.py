"""Polynomial-time reduction from Vertex Cover to Independent Set.

A set S is a vertex cover of G = (V, E) if and only if V \\ S is an
independent set of G:

  * If S covers every edge, then no edge has both endpoints outside S,
    so V \\ S contains no edge, i.e. V \\ S is independent.
  * Conversely, if I is independent, every edge has at least one endpoint
    not in I, so V \\ I is a vertex cover.

Therefore G has a vertex cover of size AT MOST k exactly when G has an
independent set of size AT LEAST n - k.  The reduction keeps the graph
unchanged and maps the threshold k to n - k, which is computable in
polynomial (indeed linear) time.
"""


def reduce(instance):
    """Reduce a Vertex Cover instance to an Independent Set instance.

    Input : {"n": n, "edges": [[u, v], ...], "k": k}   (Vertex Cover)
    Output: {"n": n, "edges": [[u, v], ...], "k": n - k} (Independent Set)

    The graph is identical; only the threshold is complemented.  This is
    correct for every integer k, including the documented edge cases
    (k < 0, k >= n, and edgeless graphs).
    """
    n = instance["n"]
    edges = [list(edge) for edge in instance["edges"]]
    k = instance["k"]

    # Complement of a vertex cover is an independent set, so a cover of
    # size <= k exists iff an independent set of size >= n - k exists.
    return {"n": n, "edges": edges, "k": n - k}
