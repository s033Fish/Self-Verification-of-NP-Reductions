"""Polynomial-time reduction from Vertex Cover to Clique.

Given a Vertex Cover instance
    {"n": n, "edges": [[u, v], ...], "k": k}
we build the complement graph on the same vertex set and ask for a clique
of size n - k.

Correctness:
    A set S is a vertex cover of G iff V \ S is an independent set in G.
    An independent set in G is exactly a clique in the complement graph.
    Thus G has a vertex cover of size at most k
        iff complement(G) has a clique of size at least n - k.

The construction uses O(n^2) time and space, so it is polynomial.
"""


def reduce(instance):
    """Return a Clique instance that is yes iff the Vertex Cover instance is yes."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Record the original edges as unordered pairs so we can take the complement.
    present = set()
    for u, v in edges:
        if u > v:
            u, v = v, u
        present.add((u, v))

    # Build every non-edge of the source graph; these are the edges of the
    # complement graph, in which a clique is an independent set of the source.
    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in present:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": n - k}
