"""Polynomial-time reduction from Vertex Cover to Clique.

Given a Vertex Cover instance (G, k) with n vertices, build the complement
graph G' on the same vertex set and set k' = n - k.

Correctness:
  G has a vertex cover of size <= k
    <=> G has an independent set of size >= n - k
    <=> the complement G' has a clique of size >= n - k.

Edge cases:
  * k < 0: source is no; k' = n - k > n, target is no (k' > n).
  * k >= n: source is yes; k' = n - k <= 0, target is yes.
  * no edges: source yes for k >= 0; G' is complete, and k' = n - k <= n,
    so it has a clique of size k' (target yes).
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    existing = set()
    for u, v in edges:
        if u > v:
            u, v = v, u
        existing.add((u, v))

    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in existing:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": n - k}
