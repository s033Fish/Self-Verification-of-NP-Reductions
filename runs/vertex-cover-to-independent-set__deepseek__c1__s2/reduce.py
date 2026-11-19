"""Polynomial-time reduction from Vertex Cover to Independent Set.

Key fact: a set S is a vertex cover of G iff V \\ S is an independent set of G.
Therefore G has a vertex cover of size AT MOST k iff G has an independent set
of size AT LEAST n - k.  The reduction keeps the graph unchanged and maps the
budget k to n - k.

Edge cases:
  * k < 0      -> n - k > n, and Independent Set answers no for k > n.
  * k >= n     -> n - k <= 0, and Independent Set answers yes for k <= 0.
  * no edges   -> Independent Set is yes for any k <= n, matching Vertex Cover.
"""

from __future__ import annotations


def reduce(instance):
    """Map a Vertex Cover instance to an Independent Set instance.

    Instance format (both problems):
        {"n": n, "edges": [[u, v], ...], "k": k}
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Same graph; the complement of a vertex cover is an independent set.
    return {"n": n, "edges": [list(e) for e in edges], "k": n - k}
