"""Polynomial-time reduction from Clique to Vertex Cover.

A clique in G is an independent set in the complement graph complement(G).
The complement of an independent set is a vertex cover, so:

    G has a clique of size at least k
        <=> complement(G) has an independent set of size at least k
        <=> complement(G) has a vertex cover of size at most n - k.

Therefore the reduction maps (G, k) to (complement(G), n - k).
"""


def reduce(instance):
    """Reduce a Clique instance to a Vertex Cover instance.

    Input:  {"n": n, "edges": [[u, v], ...], "k": k}  (Clique)
    Output: {"n": n, "edges": [[u, v], ...], "k": n - k}  (Vertex Cover)
    """
    n = instance["n"]
    k = instance["k"]

    # Normalize the input edges as unordered pairs with u < v.
    present = set()
    for u, v in instance["edges"]:
        if u > v:
            u, v = v, u
        present.add((u, v))

    # Build the complement graph: every pair 0 <= u < v < n that is not an
    # edge of the input graph.  This is O(n^2) time and output size.
    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in present:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": n - k}
