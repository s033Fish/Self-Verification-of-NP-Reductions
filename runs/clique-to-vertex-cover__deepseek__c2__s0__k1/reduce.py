"""Polynomial-time reduction from Clique to Vertex Cover.

A clique in G is an independent set in the complement graph complement(G).
A set S is an independent set in a graph H iff V(H) \ S is a vertex cover
of H.  Therefore G has a clique of size at least k iff complement(G) has a
vertex cover of size at most n - k.

Reduction: (n, edges, k) -> (n, complement_edges, n - k).
"""

from itertools import combinations


def reduce(instance):
    """Map a Clique instance to a Vertex Cover instance with the same answer.

    Input:  {"n": n, "edges": [[u, v], ...], "k": k}   (Clique)
    Output: {"n": n, "edges": [[u, v], ...], "k": n-k} (Vertex Cover)
    """
    n = instance["n"]
    k = instance["k"]

    # Build the set of undirected edges present in the input graph.
    # frozenset makes the representation independent of endpoint order.
    present = {frozenset(edge) for edge in instance["edges"]}

    # Complement graph on the same vertex set 0..n-1.
    complement_edges = [
        [u, v]
        for u, v in combinations(range(n), 2)
        if frozenset((u, v)) not in present
    ]

    return {"n": n, "edges": complement_edges, "k": n - k}
