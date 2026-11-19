r"""Polynomial-time reduction from Vertex Cover to Independent Set.

Key fact: a vertex set S is a vertex cover of G = (V, E) if and only if its
complement V \ S is an independent set.  Therefore G has a vertex cover of
size AT MOST k iff G has an independent set of size AT LEAST n - k.

So the reduction keeps the same graph and maps k -> n - k.
"""

from __future__ import annotations


def reduce(instance: dict) -> dict:
    """Map a Vertex Cover instance to an Independent Set instance.

    Input:  {"n": n, "edges": [[u, v], ...], "k": k}   (Vertex Cover)
    Output: {"n": n, "edges": [[u, v], ...], "k": n-k} (Independent Set)
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    return {"n": n, "edges": [list(e) for e in edges], "k": n - k}
