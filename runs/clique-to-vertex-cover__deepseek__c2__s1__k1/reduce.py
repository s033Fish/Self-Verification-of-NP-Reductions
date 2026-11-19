"""Polynomial-time reduction from Clique to Vertex Cover.

A clique of size at least k in G is exactly an independent set of size at
least k in the complement graph G'.  A set S is an independent set in G'
iff its complement V \\ S is a vertex cover of G'.  Hence:

    G has a clique of size >= k
        <=> G' has an independent set of size >= k
        <=> G' has a vertex cover of size <= n - k.

So the reduction maps (n, edges, k) to (n, complement_edges, n - k).
This also handles the edge cases: k <= 0 gives target k' >= n (always yes),
and k > n gives target k' < 0 (always no).
"""

from itertools import combinations


def reduce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    present = {frozenset((u, v)) for u, v in edges}
    complement_edges = [
        [u, v]
        for u, v in combinations(range(n), 2)
        if frozenset((u, v)) not in present
    ]

    return {"n": n, "edges": complement_edges, "k": n - k}
