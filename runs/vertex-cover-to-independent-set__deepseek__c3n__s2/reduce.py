"""Polynomial-time reduction from Vertex Cover to Independent Set.

Key fact: a set S is a vertex cover of G iff its complement V \\ S is an
independent set of G.  Therefore G has a vertex cover of size AT MOST k
iff G has an independent set of size AT LEAST n - k.

The reduction keeps the graph unchanged and maps k -> n - k.
"""

from __future__ import annotations


def reduce(instance: dict) -> dict:
    """Reduce a Vertex Cover instance to an Independent Set instance.

    Input : {"n": n, "edges": [[u, v], ...], "k": k}   (Vertex Cover)
    Output: {"n": n, "edges": [[u, v], ...], "k": n-k} (Independent Set)

    Correctness: S is a vertex cover of G iff V \\ S is independent, so
    G has a cover of size <= k iff G has an independent set of size >= n-k.
    Runs in polynomial time (linear in the size of the instance).
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    return {"n": n, "edges": [list(edge) for edge in edges], "k": n - k}
