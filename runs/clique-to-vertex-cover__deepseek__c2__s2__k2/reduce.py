"""Polynomial-time reduction from Clique to Vertex Cover.

Clique instance:        {"n": n, "edges": [[u, v], ...], "k": k}
Vertex Cover instance:  {"n": n, "edges": [[u, v], ...], "k": k}

Reduction
---------
Given a Clique instance (G, k), return the Vertex Cover instance
(complement(G), n - k).

Why it is correct
-----------------
A set S is a clique in G iff every pair of distinct vertices in S is an
edge of G, i.e. iff no pair of distinct vertices in S is a non-edge of G.
Non-edges of G are exactly the edges of complement(G).  So S is a clique
in G iff V \\ S contains at least one endpoint of every edge of
complement(G), i.e. iff V \\ S is a vertex cover of complement(G).

Therefore G has a clique of size >= k iff complement(G) has a vertex cover
of size <= n - k.  The edge cases line up as well:
  * k <= 0  -> n - k >= n, and any graph has a vertex cover of size <= n
               (all vertices), so the target answer is yes.
  * k > n   -> n - k < 0, and Vertex Cover is always no for k < 0.
  * k = 1, n >= 1 -> n - 1 >= 0 and the target is yes (a single vertex
               covers nothing but the budget allows it; the empty set works
               when there are no edges), matching "clique of size 1 exists".

The reduction runs in O(n^2) time and O(n^2) space.
"""


def reduce(instance):
    """Reduce a Clique instance to a Vertex Cover instance."""
    n = instance["n"]
    k = instance["k"]

    # Collect the existing (undirected) edges of G.
    present = set()
    for u, v in instance["edges"]:
        present.add((u, v) if u < v else (v, u))

    # Edges of the complement graph: all pairs not present in G.
    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in present:
                complement_edges.append([u, v])

    # A clique of size >= k in G becomes a vertex cover of size <= n - k
    # in the complement graph.
    return {"n": n, "edges": complement_edges, "k": n - k}
