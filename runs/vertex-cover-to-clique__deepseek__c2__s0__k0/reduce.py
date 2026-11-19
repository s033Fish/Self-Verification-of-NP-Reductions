"""Polynomial-time reduction from Vertex Cover to Clique.

Given a Vertex Cover instance G = (V, E), k, build the complement graph
G' = (V, E') where E' contains exactly the non-edges of G.  Then:

    G has a vertex cover of size at most k
      <=> V minus that cover is an independent set of size at least n - k
      <=> G' has a clique of size at least n - k.

So the Clique instance is (G', n - k).
"""


def _normalize_edge(u, v):
    return (u, v) if u < v else (v, u)


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    present = set()
    for u, v in edges:
        present.add(_normalize_edge(u, v))

    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in present:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": n - k}
