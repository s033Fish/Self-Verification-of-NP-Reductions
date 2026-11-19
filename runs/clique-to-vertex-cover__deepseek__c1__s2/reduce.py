"""Polynomial-time reduction from Clique to Vertex Cover.

Given a Clique instance ``{"n": n, "edges": E, "k": k}`` on graph G, build the
complement graph G' on the same vertex set and output the Vertex Cover instance
``{"n": n, "edges": E', "k": n - k}``.

Correctness
-----------
A set C is a vertex cover of G' iff V \\ C is an independent set of G'.  An
independent set in G' is exactly a clique in G.  Hence G has a clique of size
at least k iff G' has an independent set of size at least k iff G' has a vertex
cover of size at most n - k.

The edge cases line up as well:
  * k <= 0: Clique is yes; the target parameter n - k >= n, and a vertex cover
    of size at most n - k always exists (all n vertices suffice).
  * k > n: Clique is no; the target parameter n - k < 0, and Vertex Cover is
    always no for a negative budget.
  * k = 1 with n >= 1: Clique is yes; n - 1 vertices cover G' because G' has
    at least one non-edge (indeed any single vertex is an independent set).
"""

from itertools import combinations


def reduce(instance):
    """Return a Vertex Cover instance equivalent to the Clique instance."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Edges of the complement graph: every non-edge of the input graph.
    original = {frozenset((u, v)) for u, v in edges}
    complement_edges = [
        [u, v] for u, v in combinations(range(n), 2) if frozenset((u, v)) not in original
    ]

    return {"n": n, "edges": complement_edges, "k": n - k}
