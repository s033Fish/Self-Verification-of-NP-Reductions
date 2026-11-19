"""Polynomial-time reduction from Independent Set to Vertex Cover.

Key fact: for any graph G = (V, E), a set S is an independent set if and only
if its complement V \\ S is a vertex cover.  Indeed, S has no edge with both
endpoints in S exactly when every edge has at least one endpoint outside S.

Consequently, for n = |V|:

    G has an independent set of size >= k
        <=> G has a vertex cover of size <= n - k.

So the reduction keeps the graph (n and edges) unchanged and maps k to n - k.

This is correct for every integer k, including the edge cases:
  * k <= 0: the source is yes; the target has k' = n - k >= n, and any graph
    has a vertex cover of size at most n (all vertices), so it is yes.
  * k > n: the source is no; the target has k' = n - k < 0, and a vertex cover
    of negative size is impossible, so it is no.
"""


def reduce(instance):
    """Reduce an Independent Set instance to a Vertex Cover instance.

    Input/output format: {"n": n, "edges": [[u, v], ...], "k": k}
    """
    n = instance["n"]
    k = instance["k"]
    return {
        "n": n,
        "edges": [list(edge) for edge in instance["edges"]],
        "k": n - k,
    }
