"""Polynomial-time reduction from Independent Set to Clique.

An independent set in a graph G is exactly a clique in the complement graph
G-bar (same vertex set, edges between exactly the non-adjacent pairs of G).
So the reduction keeps n and k and replaces the edge set with its complement.
"""

from __future__ import annotations


def reduce(instance):
    """Reduce an Independent Set instance to a Clique instance.

    Input:  {"n": n, "edges": [[u, v], ...], "k": k}
    Output: {"n": n, "edges": [[u, v], ...], "k": k}

    The output graph is the complement of the input graph on the same n
    vertices, with the same k.  A set S is independent in G iff S is a clique
    in the complement, so the yes/no answers coincide (including the k <= 0
    and k > n edge cases).
    """
    n = instance["n"]
    edges = instance["edges"]

    # Existing edges, stored as frozensets so orientation does not matter.
    present = {frozenset((u, v)) for u, v in edges}

    complement = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in present:
                complement.append([u, v])

    return {"n": n, "edges": complement, "k": instance["k"]}
