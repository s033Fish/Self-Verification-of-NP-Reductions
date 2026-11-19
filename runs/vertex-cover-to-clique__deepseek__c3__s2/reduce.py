"""Polynomial-time reduction from Vertex Cover to Clique.

Reduction: a vertex cover of size <= k in G exists iff the complement
graph of G has a clique of size >= n - k.

Proof sketch: C is a vertex cover of G iff V \\ C is an independent set in
G iff V \\ C is a clique in the complement graph.  Thus a cover of size at
most k exists iff an independent set of size at least n - k exists iff a
clique of size at least n - k exists in the complement.
"""

from itertools import combinations


def reduce(instance):
    """Map a Vertex Cover instance to a Clique instance.

    Input : {"n": n, "edges": [[u, v], ...], "k": k}
    Output: {"n": n, "edges": complement_edges, "k": n - k}
    """
    n = instance["n"]
    edges = instance["edges"]

    present = set()
    for u, v in edges:
        present.add((u, v) if u < v else (v, u))

    complement_edges = [
        [u, v] for u, v in combinations(range(n), 2) if (u, v) not in present
    ]

    return {"n": n, "edges": complement_edges, "k": n - instance["k"]}
