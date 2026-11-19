"""Polynomial-time reduction from Independent Set to Clique.

Given an Independent Set instance G = (V, E) with threshold k, the target
Clique instance is the complement graph G' = (V, V x V \ E) with the same
threshold k.  A set S is independent in G iff every pair of distinct vertices
in S is non-adjacent in G, i.e. every pair is adjacent in G', i.e. S is a
clique in G'.  Hence G has an independent set of size at least k iff G' has a
clique of size at least k.

The construction uses O(n^2) time and space, so it is polynomial.
"""


def reduce(instance):
    """Map an Independent Set instance to a Clique instance.

    Both problems use the instance format:
        {"n": n, "edges": [[u, v], ...], "k": k}

    The returned instance has the same ``n`` and ``k`` and contains exactly
    the edges missing from the input graph (its complement).
    """
    n = instance["n"]
    k = instance["k"]

    # Normalize the input edges as unordered pairs.  The documented format
    # already forbids duplicates and self-loops, but normalizing makes the
    # construction robust to [v, u] orderings.
    present = set()
    for edge in instance["edges"]:
        u, v = edge[0], edge[1]
        if u == v:
            continue
        if u > v:
            u, v = v, u
        present.add((u, v))

    # The complement contains every pair u < v that is not an input edge.
    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in present:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": k}
