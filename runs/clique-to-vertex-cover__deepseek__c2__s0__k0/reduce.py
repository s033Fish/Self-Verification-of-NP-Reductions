"""Polynomial-time reduction from Clique to Vertex Cover.

Given a Clique instance
    {"n": n, "edges": [[u, v], ...], "k": k}
we build the complement graph H on the same vertex set 0..n-1 and output the
Vertex Cover instance
    {"n": n, "edges": complement_edges, "k": n - k}.

Correctness:
    A set C is a vertex cover of H
        iff V \\ C is an independent set in H
        iff V \\ C is a clique in G.
    Hence G has a clique of size at least k
        iff H has a vertex cover of size at most n - k.

The construction is polynomial: it examines O(n^2) vertex pairs.
"""


def reduce(instance):
    """Reduce a Clique instance to a Vertex Cover instance."""
    n = instance["n"]
    k = instance["k"]

    # Normalize the given edges (undirected, no self-loops) into a set.
    given = set()
    for u, v in instance["edges"]:
        if u > v:
            u, v = v, u
        given.add((u, v))

    # Edges of the complement graph: all pairs not present in G.
    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in given:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": n - k}
