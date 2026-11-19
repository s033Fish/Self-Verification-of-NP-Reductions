"""Polynomial-time reduction from Independent Set to Vertex Cover.

Key fact: for any graph G = (V, E), a set S is an independent set of G
if and only if its complement V \\ S is a vertex cover of G.

Proof:
  * If S is independent, then every edge has at least one endpoint outside
    S (otherwise both endpoints would lie in S, contradicting independence),
    so V \\ S covers every edge.
  * If C is a vertex cover, then no edge has both endpoints in V \\ C,
    so V \\ C is independent.

Therefore G has an independent set of size AT LEAST k
iff G has a vertex cover of size AT MOST n - k.

The reduction keeps the graph unchanged and maps k -> n - k.  It is O(1)
work beyond copying the instance (polynomial time), and it does not call
any brute-force solver.

Edge cases line up exactly:
  * k <= 0:  source yes.  k' = n - k >= n, and a cover of size >= n is
    always achievable (all vertices), so target yes.
  * k > n:   source no.   k' = n - k < 0, and a cover of size < 0 is
    impossible, so target no.
  * no edges: source yes for every k <= n.  k' = n - k >= 0 and the empty
    set covers a graph with no edges, so target yes.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce an Independent Set instance to a Vertex Cover instance.

    Input : {"n": n, "edges": [[u, v], ...], "k": k}   (Independent Set)
    Output: {"n": n, "edges": [[u, v], ...], "k": n-k} (Vertex Cover)

    The answer to the output is yes exactly when the answer to the input
    is yes.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # A set S is independent iff V \ S is a vertex cover, so the threshold
    # "at least k" for Independent Set becomes "at most n - k" for Vertex
    # Cover.
    return {
        "n": n,
        "edges": [list(edge) for edge in edges],
        "k": n - k,
    }
