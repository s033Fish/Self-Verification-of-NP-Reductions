"""Polynomial-time reduction from Clique to Vertex Cover.

A set S is a clique in G exactly when S is an independent set in the
complement graph G'.  A set C is a vertex cover of G' exactly when its
complement V \\ C is an independent set in G'.  Therefore G has a clique of
size at least k iff G' has a vertex cover of size at most n - k.

So the reduction builds the complement graph and maps the parameter k to
n - k.  This also handles the documented edge cases:

  * k <= 0: the source is always yes, and n - k >= n is >= n, so the
    target is always yes.
  * k > n: the source is always no, and n - k < 0, so the target is
    always no.
  * k = 1 with n >= 1: the target parameter is n - 1, and every graph on
    n >= 1 vertices has a vertex cover of size at most n - 1.
"""


def reduce(instance):
    """Reduce a Clique instance to a Vertex Cover instance.

    The input and output both have the form
    {"n": n, "edges": [[u, v], ...], "k": k}.
    """
    n = instance["n"]
    k = instance["k"]

    # Build the complement graph on the same vertex set 0..n-1.
    present = set()
    for u, v in instance["edges"]:
        if u > v:
            u, v = v, u
        present.add((u, v))

    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in present:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": n - k}
