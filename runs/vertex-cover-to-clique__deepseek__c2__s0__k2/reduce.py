"""Polynomial-time reduction from Vertex Cover to Clique.

A set S is a vertex cover of G iff V \\ S is an independent set of G,
i.e. V \\ S is a clique in the complement graph complement(G).

Hence G has a vertex cover of size AT MOST k
  iff complement(G) has a clique of size AT LEAST n - k.

So the reduction maps (n, edges, k) -> (n, complement_edges, n - k).

Edge cases check out:
  * k < 0: VC is no; target k' = n - k > n, Clique is no.
  * no edges, k >= 0: complement is complete, clique size n >= n - k, yes.
  * k >= n: VC is yes; target k' = n - k <= 0, Clique is yes.
"""


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Build the set of existing (undirected) edges.
    existing = set()
    for u, v in edges:
        existing.add((u, v) if u < v else (v, u))

    # Complement graph: all pairs {u, v}, u < v, that are not edges of G.
    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in existing:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": n - k}
