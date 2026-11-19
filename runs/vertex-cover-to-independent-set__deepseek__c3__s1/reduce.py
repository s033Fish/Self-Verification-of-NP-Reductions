"""Polynomial-time reduction from Vertex Cover to Independent Set.

Key fact: a set S is a vertex cover of G iff its complement V \\ S is an
independent set of G.  Therefore G has a vertex cover of size at most k iff
G has an independent set of size at least n - k.

So the reduction keeps the graph unchanged and maps the threshold k to n - k.
This is valid for every integer k, including the edge cases k < 0 and k > n.
"""

from __future__ import annotations

from typing import Any

Instance = dict[str, Any]


def reduce(instance: Instance) -> Instance:
    """Reduce a Vertex Cover instance to an Independent Set instance.

    Input:  {"n": n, "edges": [[u, v], ...], "k": k}
    Output: {"n": n, "edges": [[u, v], ...], "k": n - k}
    """
    n = instance["n"]
    edges = [[u, v] for u, v in instance["edges"]]
    k = instance["k"]
    return {"n": n, "edges": edges, "k": n - k}
