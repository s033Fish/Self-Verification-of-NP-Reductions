r"""Polynomial-time reduction from Independent Set to Vertex Cover.

A set S is an independent set in G = (V, E) if and only if its complement
V \ S is a vertex cover: an edge has both endpoints in S exactly when it is
not covered by V \ S.  Hence G has an independent set of size >= k iff G has
a vertex cover of size <= n - k.

So the reduction keeps the same graph and maps the threshold k to n - k.
"""

from __future__ import annotations


def reduce(instance: dict) -> dict:
    """Map an Independent Set instance to a Vertex Cover instance."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Same graph; complement of an independent set is a vertex cover.
    return {
        "n": n,
        "edges": [list(edge) for edge in edges],
        "k": n - k,
    }
