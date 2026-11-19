"""Polynomial-time reduction from Clique to Vertex Cover.

A clique in G is an independent set in the complement graph G'.  A set S is a
vertex cover of G' iff its complement V \\ S is an independent set of G'.
Therefore G has a clique of size at least k iff G' has a vertex cover of size
at most n - k.

The reduction simply builds the complement graph and maps k -> n - k.
"""


def reduce(instance):
    """Map a Clique instance to a Vertex Cover instance.

    Input:  {"n": n, "edges": [[u, v], ...], "k": k}
    Output: {"n": n, "edges": [[u, v], ...], "k": n - k}
            where the output edges are exactly the non-edges of the input
            graph (the complement graph on the same vertex set).
    """
    n = instance["n"]
    k = instance["k"]

    # Normalise the given undirected edges so that (u, v) is stored with u < v.
    present = set()
    for edge in instance["edges"]:
        u, v = edge[0], edge[1]
        if u > v:
            u, v = v, u
        present.add((u, v))

    # Build the complement: every unordered pair {u, v}, u < v, not present.
    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in present:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": n - k}
