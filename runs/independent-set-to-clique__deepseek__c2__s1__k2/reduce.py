"""Polynomial-time reduction from Independent Set to Clique.

An independent set in a graph G is exactly a clique in the complement graph
of G.  So we map an Independent Set instance (G, k) to the Clique instance
(complement(G), k).  The number of vertices n and the threshold k are kept
unchanged, which also preserves the edge-case behaviour for k <= 0 and k > n.
"""


def reduce(instance):
    n = instance["n"]
    k = instance["k"]

    # Collect the given edges as unordered pairs.  The input is validated by
    # the framework, so there are no self-loops or duplicate/reversed pairs.
    present = set()
    for u, v in instance["edges"]:
        if u > v:
            u, v = v, u
        present.add((u, v))

    # Edges of the complement graph: every pair u < v not present in G.
    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in present:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": k}
