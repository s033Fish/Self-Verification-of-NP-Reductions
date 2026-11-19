"""Polynomial-time reduction from Clique to Independent Set.

A set of vertices is a clique in a graph G if and only if it is an
independent set in the complement graph of G.  Therefore the reduction
keeps n and k unchanged and replaces the edge list by the list of all
pairs that are not edges of G.
"""


def reduce(instance):
    """Return the complement-graph instance for the Clique instance.

    Input and output are both dicts of the form
        {"n": n, "edges": [[u, v], ...], "k": k}
    as documented for Clique and IndependentSet.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Store undirected edges canonically so that [u, v] and [v, u] are
    # treated as the same edge.
    present = {frozenset(edge) for edge in edges}

    complement_edges = [
        [u, v]
        for u in range(n)
        for v in range(u + 1, n)
        if frozenset((u, v)) not in present
    ]

    return {"n": n, "edges": complement_edges, "k": k}
