"""Polynomial-time reduction from Vertex Cover to Independent Set.

A set S is a vertex cover of G iff its complement V \\ S is an independent
set of G (an edge is uncovered by S exactly when both endpoints lie in
V \\ S).  Hence G has a vertex cover of size AT MOST k iff G has an
independent set of size AT LEAST n - k.

So the reduction keeps the graph unchanged and maps k -> n - k.
"""

from __future__ import annotations


def reduce(instance):
    """Reduce a Vertex Cover instance to an Independent Set instance.

    Input:  {"n": n, "edges": [[u, v], ...], "k": k}
    Output: {"n": n, "edges": [[u, v], ...], "k": n - k}
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Copy edges so the returned instance shares no mutable state with input.
    new_edges = [[u, v] for (u, v) in edges]

    return {"n": n, "edges": new_edges, "k": n - k}
