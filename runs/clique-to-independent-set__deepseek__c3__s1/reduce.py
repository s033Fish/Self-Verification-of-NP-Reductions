"""Polynomial-time reduction from Clique to Independent Set.

A set of vertices is a clique in G iff it is an independent set in the
complement graph of G.  Therefore the reduction keeps n and k unchanged and
replaces the edge set by its complement (all pairs {u, v}, u < v, that are
not edges of G).
"""


def reduce(instance):
    """Map a Clique instance to an Independent Set instance.

    Input:  {"n": n, "edges": [[u, v], ...], "k": k}
    Output: {"n": n, "edges": [[u, v], ...], "k": k}

    The output graph is the complement of the input graph.
    """
    n = instance["n"]
    k = instance["k"]

    # Normalise the given edges into a set of unordered pairs.
    present = set()
    for u, v in instance["edges"]:
        if u > v:
            u, v = v, u
        present.add((u, v))

    # Complement: every pair u < v that is not an edge of the input graph.
    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in present:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": k}
