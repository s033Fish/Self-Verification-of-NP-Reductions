"""Polynomial-time reduction from Independent Set to Vertex Cover.

Given an Independent Set instance ``{"n": n, "edges": edges, "k": k}``,
return the Vertex Cover instance on the same graph with parameter
``n - k``.

Correctness: a set S is an independent set in G iff V \\ S is a vertex
cover of G.  Therefore G has an independent set of size at least k iff G
has a vertex cover of size at most n - k.  The construction runs in
linear time in the size of the input.
"""

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce Independent Set to Vertex Cover.

    The graph is unchanged; the target budget is ``n - k``.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Copy the edges so the returned instance shares no mutable structure
    # with the input instance.
    return {
        "n": n,
        "edges": [list(edge) for edge in edges],
        "k": n - k,
    }
