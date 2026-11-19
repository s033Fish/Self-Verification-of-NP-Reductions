"""Polynomial-time reduction from Clique to Independent Set.

A set S of vertices is a clique in G exactly when S is an independent set in
the complement graph G'.  Therefore we map an instance (G, k) of Clique to the
instance (G', k) of Independent Set, where G' has the same vertex set and an
edge between every pair of distinct vertices that is NOT an edge of G.

This preserves the yes/no answer for all cases, including the edge cases:
  * k <= 0: both are always yes.
  * k > n : both are always no.
  * k = 1: a single vertex is both a clique and an independent set.
"""


def reduce(instance):
    n = instance["n"]
    k = instance["k"]

    # Normalise the given edges to an unordered set of pairs.
    present = set()
    for u, v in instance["edges"]:
        if u == v:
            continue
        present.add((u, v) if u < v else (v, u))

    # Complement graph: every distinct pair not present in the original graph.
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in present:
                edges.append([u, v])

    return {"n": n, "edges": edges, "k": k}
