"""Polynomial-time reduction from Independent Set to Clique.

An independent set in a graph G is exactly a clique in the complement
graph of G.  Therefore, given an Independent Set instance
``{"n": n, "edges": edges, "k": k}``, we output the Clique instance on
the complement graph with the same ``n`` and ``k``.

The complement is built in O(n^2) time, so the reduction is polynomial.
No brute-force solver is used.
"""


def reduce(instance):
    """Map an Independent Set instance to a Clique instance.

    The returned instance is yes for Clique iff the input instance is yes
    for Independent Set.
    """
    n = instance["n"]
    k = instance["k"]

    # Normalize the given edges to a set of frozensets so that duplicate
    # or reversed representations are handled robustly.
    given = set()
    for u, v in instance["edges"]:
        given.add(frozenset((u, v)))

    # Complement graph: include every non-loop pair {u, v} not in the
    # original graph.
    complement_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in given:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": k}
