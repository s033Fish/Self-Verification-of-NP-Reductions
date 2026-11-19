"""Reduction from 3-Coloring to Independent Set.

Given an instance of ThreeColoring (a graph G = (V, E)), we construct a new
graph G' = (V', E') and an integer k such that G is 3‑colorable iff G' has an
independent set of size at least k.

Construction (standard textbook reduction):
  * For each original vertex v ∈ V we create three vertices v_0, v_1, v_2 in
    V'. They form a triangle, guaranteeing that an independent set can contain
    at most one of them.
  * For each original edge {u, v} ∈ E we add edges between the same‑colour
    copies: (u_0, v_0), (u_1, v_1), (u_2, v_2). This forbids two adjacent
    original vertices from being assigned the same colour.
  * Set k = |V|. Selecting exactly one vertex from each triangle yields an
    independent set of size k, and the colour‑conflict edges ensure that the
    selections correspond to a proper 3‑colouring of G.

The reduction runs in time O(|V| + |E|) and produces a valid IndependentSet
instance.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ThreeColoring, IndependentSet


def reduce(instance: Dict) -> Dict:
    """Reduce a ThreeColoring instance to an IndependentSet instance.

    Parameters
    ----------
    instance: dict
        A valid ThreeColoring instance (validated by ``ThreeColoring.validate``).

    Returns
    -------
    dict
        A valid IndependentSet instance where ``n = 3 * original_n`` and
        ``k = original_n``.
    """
    # Validate the source instance to catch malformed input early.
    ThreeColoring.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # New graph has three vertices per original vertex.
    new_n = n * 3
    new_edges: List[List[int]] = []

    # Add triangle edges for each original vertex.
    for v in range(n):
        a = v * 3
        b = v * 3 + 1
        c = v * 3 + 2
        new_edges.append([a, b])
        new_edges.append([a, c])
        new_edges.append([b, c])

    # Add same‑colour conflict edges for each original edge.
    for u, v in edges:
        for colour in range(3):
            new_edges.append([u * 3 + colour, v * 3 + colour])

    # Independent set size we require.
    k = n

    reduced_instance = {"n": new_n, "edges": new_edges, "k": k}

    # Ensure the produced instance conforms to the target specification.
    IndependentSet.validate(reduced_instance)
    return reduced_instance

