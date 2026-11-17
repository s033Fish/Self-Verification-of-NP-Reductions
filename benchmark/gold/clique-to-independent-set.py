"""Gold reduction: Clique -> Independent Set.        [difficulty: 2 of 6]

SOURCE  Clique           {"n": n, "edges": [[u, v], ...], "k": k}
        yes iff some k vertices are pairwise adjacent.
TARGET  Independent Set  {"n": n, "edges": [[u, v], ...], "k": k}
        yes iff some k vertices are pairwise NON-adjacent.

Construction
  1. Build the complement graph: same vertices 0..n-1, and an edge [u, v]
     (u < v) exactly when [u, v] is NOT an edge of the original graph.
  2. A set of vertices is a clique in G iff it is independent in the
     complement, so k stays the same.
"""


def reduce(instance):
    n = instance["n"]
    edges = {tuple(edge) for edge in instance["edges"]}
    k = instance["k"]

    inverse_edges = []

    for i in range(n):
        for j in range(i, n):
            if i == j:
                continue

            if not (i, j) in edges and not (j, i) in edges:
                inverse_edges.append((i, j)) 

    return {"n": n, "edges": inverse_edges, "k": k}