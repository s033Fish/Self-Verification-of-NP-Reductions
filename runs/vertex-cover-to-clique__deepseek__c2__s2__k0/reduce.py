"""Polynomial-time reduction from Vertex Cover to Clique.

A set S is a vertex cover of G iff V \\ S is an independent set of G.
An independent set of G is exactly a clique of the complement graph
G-bar.  Therefore G has a vertex cover of size at most k iff G-bar has a
clique of size at least n - k.

So the reduction maps (n, edges, k) to (n, complement_edges, n - k).
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Normalise the given edges into a set of unordered pairs.
    present = set()
    for u, v in edges:
        if u > v:
            u, v = v, u
        present.add((u, v))

    # Build the complement graph: [u, v] for every non-edge with u < v.
    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in present:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": n - k}
