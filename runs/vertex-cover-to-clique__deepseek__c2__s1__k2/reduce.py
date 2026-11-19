"""Polynomial-time reduction from Vertex Cover to Clique.

A set S is a vertex cover of G iff V \\ S is an independent set of G,
iff V \\ S is a clique of the complement graph of G.

Hence G has a vertex cover of size at most k
  <=> G has an independent set of size at least n - k
  <=> the complement of G has a clique of size at least n - k.

So we map (G, k) -> (complement(G), n - k).
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Build the set of existing (normalized) edges.
    existing = set()
    for u, v in edges:
        if u > v:
            u, v = v, u
        existing.add((u, v))

    # Complement graph: all pairs not present as an edge.
    comp_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in existing:
                comp_edges.append([u, v])

    return {"n": n, "edges": comp_edges, "k": n - k}
