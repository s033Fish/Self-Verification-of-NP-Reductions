"""Polynomial-time reduction from Clique to Vertex Cover.

Standard complement-graph reduction:

    G has a clique of size >= k
        <=> the complement graph G' has an independent set of size >= k
        <=> G' has a vertex cover of size <= n - k

because a vertex cover of G' is exactly the complement of an independent
set of G', so  min vertex cover(G') = n - max independent set(G') and the
maximum independent set of G' equals the maximum clique of G.

So reduce(G, k) = (complement(G), n - k).

Edge cases:
  * k <= 0  -> target k' = n - k >= n, and a vertex cover of size >= n is
    always achievable (all vertices), so target is yes, matching source.
  * k > n   -> target k' = n - k < 0, and a cover of negative size is
    impossible, so target is no, matching source.
  * k = 1 and n >= 1 -> target k' = n - 1; since max clique >= 1, the
    minimum vertex cover is n - maxclique <= n - 1, so target is yes.
"""

from __future__ import annotations


def reduce(instance):
    """Reduce a Clique instance to a Vertex Cover instance."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    original = {frozenset((u, v)) for u, v in edges}

    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in original:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": n - k}
