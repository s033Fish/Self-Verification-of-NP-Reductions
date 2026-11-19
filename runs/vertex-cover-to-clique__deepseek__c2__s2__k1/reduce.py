"""Polynomial-time reduction from Vertex Cover to Clique.

A set S is a vertex cover of G iff V \\ S is an independent set in G,
i.e. a clique in the complement graph of G.  Therefore G has a vertex
cover of size at most k iff the complement of G has a clique of size at
least n - k.

So the reduction maps (G, k) to (complement(G), n - k).
"""


def reduce(instance):
    n = instance["n"]
    k = instance["k"]
    edges = instance["edges"]

    # Build the set of existing (undirected) edges, normalized as (min, max).
    present = set()
    for u, v in edges:
        if u > v:
            u, v = v, u
        present.add((u, v))

    # Complement graph: all pairs 0 <= u < v < n that are not edges of G.
    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in present:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": n - k}
