"""Polynomial-time reduction from Independent Set to Vertex Cover.

A set S of vertices is an independent set in G = (V, E) if and only if its
complement V \\ S is a vertex cover of G:

  * If S is independent, then no edge has both endpoints in S, so every edge
    has at least one endpoint outside S, i.e. V \\ S is a vertex cover.
  * If C is a vertex cover, then no edge has both endpoints outside C, so C's
    complement is independent.

Consequently G has an independent set of size >= k iff G has a vertex cover of
size <= n - k.  So the reduction keeps n and edges unchanged and maps k to
n - k.

Edge cases:
  * k <= 0: source is always yes; target k' = n - k >= n, and Vertex Cover is
    yes whenever k' >= n.  Correct.
  * k > n: source is always no; target k' = n - k < 0, and Vertex Cover is no
    whenever k' < 0.  Correct.
  * No edges: source is yes iff k <= n; target k' = n - k >= 0 iff k <= n, and
    an edgeless graph is coverable by the empty set for every k' >= 0.  Correct.

The transformation only reads the input and computes n - k, so it runs in
polynomial time (linear in the size of the instance) and never invokes any
brute-force solver.
"""


def reduce(instance):
    """Reduce an Independent Set instance to a Vertex Cover instance.

    Input:  {"n": n, "edges": [[u, v], ...], "k": k}
    Output: {"n": n, "edges": [[u, v], ...], "k": n - k}
    """
    n = instance["n"]
    k = instance["k"]
    edges = [list(edge) for edge in instance["edges"]]
    return {"n": n, "edges": edges, "k": n - k}
