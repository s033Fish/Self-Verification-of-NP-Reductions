"""Polynomial-time reduction from Clique to Independent Set.

A set S of vertices is a clique in G iff S is an independent set in the
complement graph of G.  Therefore the reduction keeps n and k unchanged and
replaces the edge set by its complement.
"""


def reduce(instance):
    """Reduce a Clique instance to an Independent Set instance.

    Input/output format:
        {"n": n, "edges": [[u, v], ...], "k": k}
    """
    n = instance["n"]
    k = instance["k"]

    # Normalise the given undirected edges to tuples u < v.
    given = set()
    for u, v in instance["edges"]:
        if u > v:
            u, v = v, u
        given.add((u, v))

    # The complement graph: all pairs u < v that are not edges of G.
    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in given:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": k}
