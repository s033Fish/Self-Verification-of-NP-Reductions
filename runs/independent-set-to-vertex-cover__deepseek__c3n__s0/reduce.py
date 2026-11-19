r"""Polynomial-time reduction from Independent Set to Vertex Cover.

A set S is an independent set in G = (V, E) if and only if its complement
V \ S is a vertex cover of G.  Therefore G has an independent set of size
at least k exactly when G has a vertex cover of size at most n - k.

The reduction keeps the graph unchanged and maps the parameter k to n - k.
This is computable in O(|V| + |E|) time (polynomial).
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce an Independent Set instance to a Vertex Cover instance.

    Input:  {"n": n, "edges": [[u, v], ...], "k": k}   (Independent Set)
    Output: {"n": n, "edges": [[u, v], ...], "k": n-k} (Vertex Cover)

    The answer to the output is yes iff the answer to the input is yes.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Copy the edge list so the returned instance shares no mutable state
    # with the input, and normalize each edge to a fresh list.
    new_edges = [[u, v] for (u, v) in edges]

    return {"n": n, "edges": new_edges, "k": n - k}
