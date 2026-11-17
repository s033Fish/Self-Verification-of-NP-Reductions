"""Polynomial-time reduction from Clique to Independent Set.

A set S of vertices is a clique in G iff S is an independent set in the
complement graph G'.  Therefore G has a clique of size >= k exactly when
G' has an independent set of size >= k.  The reduction keeps n and k and
replaces the edge set with its complement (all non-edges of G).
"""


def reduce(instance):
    """Return the complement-graph instance of Independent Set.

    Input/output format: {"n": n, "edges": [[u, v], ...], "k": k}
    """
    n = instance["n"]
    k = instance["k"]

    # Normalize the given edges into a set of unordered pairs.
    present = set()
    for edge in instance["edges"]:
        u, v = edge[0], edge[1]
        if u == v:
            continue
        if u > v:
            u, v = v, u
        present.add((u, v))

    # The complement contains exactly the pairs not present in G.
    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in present:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": k}
