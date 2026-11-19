"""Polynomial-time reduction from Vertex Cover to Dominating Set.

Source instance: {"n": n, "edges": [[u, v], ...], "k": k}
Target instance: {"n": n', "edges": [[u, v], ...], "k": k}

Reduction (the classic "edge gadget" construction):

    For a graph G with vertex set V and edge set E, build a graph G' whose
    vertices are V (the original vertices) together with one new vertex e
    for every edge e = {u, v} of G.  The edges of G' are:

      * all original edges of G, and
      * for every edge e = {u, v} of G, the two edges {u, e}, {v, e}.

    Then

        G has a vertex cover of size <= k
            <=>  G' has a dominating set of size <= k.

    Forward: a vertex cover C dominates every edge-vertex (it covers each
    edge) and every non-isolated original vertex (which is incident to some
    edge whose other endpoint lies in C, and the original edge is present).
    Backward: a dominating set D can be turned into a vertex cover of size
    <= |D| by replacing every edge-vertex in D by one of its endpoints:
    for each edge e = {u, v}, the edge-vertex e is dominated, so e, u or v
    lies in D, and the replacement still covers e.

    The one wrinkle is isolated vertices of G: they survive as isolated
    vertices of G' and would have to belong to any dominating set, whereas
    they never belong to a minimum vertex cover.  We therefore drop isolated
    vertices from G before building the gadget.  This is safe because
    isolated vertices are in no edge, so they do not affect vertex covers.

The construction runs in O(n + m) time and space, hence is polynomial.
"""

from __future__ import annotations

from typing import Any


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    """Reduce a Vertex Cover instance to a Dominating Set instance."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Isolated vertices never matter for a vertex cover, so drop them.
    non_isolated = [False] * n
    for u, v in edges:
        non_isolated[u] = True
        non_isolated[v] = True

    # Relabel the non-isolated vertices as 0 .. num_original - 1.
    label = {}
    for v in range(n):
        if non_isolated[v]:
            label[v] = len(label)
    num_original = len(label)

    # Keep the original edges (between relabelled original vertices) ...
    new_edges: list[list[int]] = []
    for u, v in edges:
        new_edges.append([label[u], label[v]])

    # ... and add one gadget vertex per edge, adjacent to both endpoints.
    for index, (u, v) in enumerate(edges):
        gadget = num_original + index
        new_edges.append([label[u], gadget])
        new_edges.append([label[v], gadget])

    return {
        "n": num_original + len(edges),
        "edges": new_edges,
        "k": k,
    }
