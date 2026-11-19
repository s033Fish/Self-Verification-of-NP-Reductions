"""Polynomial-time reduction from Independent Set to Clique.

An independent set in a graph G is exactly a clique in the complement
graph G'.  Therefore the reduction keeps n and k unchanged and replaces
the edge set with its complement (all pairs {u, v} that are not edges
of G).

This preserves the answer for every instance, including the edge cases:
  * k <= 0: both source and target are trivially yes.
  * k > n:  both source and target are trivially no.
  * no edges: the complement is the complete graph, so any k <= n
    vertices form a clique, matching "every set is independent".
"""

from itertools import combinations


def reduce(instance):
    """Map an Independent Set instance to a Clique instance.

    Input / output format:
        {"n": n, "edges": [[u, v], ...], "k": k}
    """
    n = instance["n"]
    k = instance["k"]

    # Normalize the input edges to canonical (min, max) pairs in a set.
    # This handles either orientation and any accidental duplicates.
    existing = set()
    for edge in instance["edges"]:
        u, v = edge[0], edge[1]
        if u > v:
            u, v = v, u
        existing.add((u, v))

    # Build the complement graph: every unordered pair of distinct
    # vertices that is not an edge of the source graph.
    complement_edges = []
    for u, v in combinations(range(n), 2):
        if (u, v) not in existing:
            complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": k}
