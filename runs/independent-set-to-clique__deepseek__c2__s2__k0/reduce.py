"""Polynomial-time reduction from Independent Set to Clique.

An independent set in a graph G is exactly a clique in the complement
graph of G.  Therefore the reduction keeps n and k unchanged and replaces
the edge set by its complement (all pairs u < v that are not edges of G).
"""


def reduce(instance):
    """Reduce an Independent Set instance to a Clique instance.

    The returned instance has the same vertex set and the same k; its edges
    are precisely the non-edges of the input graph.  A set S is independent
    in the input graph iff S is a clique in the output graph, so the answers
    coincide.
    """
    n = instance["n"]
    k = instance["k"]

    present = set()
    for u, v in instance["edges"]:
        if u > v:
            u, v = v, u
        present.add((u, v))

    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in present:
                edges.append([u, v])

    return {"n": n, "edges": edges, "k": k}
