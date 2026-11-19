"""Polynomial-time reduction from Clique to Vertex Cover.

Given a Clique instance G = (V, E), k, construct the complement graph
G' = (V, E'), where E' contains exactly the unordered pairs of distinct
vertices that are not edges of G.

Then G has a clique of size at least k if and only if G' has a vertex
cover of size at most n - k.  Indeed, for any S subset of V:

    S is a clique in G  <=>  V \ S is a vertex cover in G'.

Thus the reduction returns the complement graph with target parameter
n - k.
"""


def reduce(instance):
    """Reduce a Clique instance to a Vertex Cover instance.

    The returned instance has the same vertex set and the complement edge
    set, with target parameter n - k.
    """
    n = instance["n"]
    k = instance["k"]

    # Normalize source edges to ordered pairs (min, max) so that reversed
    # duplicates are treated as the same edge.
    edge_set = set()
    for u, v in instance["edges"]:
        if u > v:
            u, v = v, u
        edge_set.add((u, v))

    # Every unordered pair of distinct vertices that is not an edge of the
    # source graph becomes an edge of the complement graph.
    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in edge_set:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": n - k}
