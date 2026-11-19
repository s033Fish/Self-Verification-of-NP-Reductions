"""Reduction from Clique to Vertex Cover.

The reduction uses the classic complement‑graph construction:

* A set of vertices forms a clique in a graph G iff its complement (the set
  of all other vertices) is a vertex cover in the complement graph \bar{G}.
* Therefore, an instance ``(G, k)`` of Clique can be transformed into the
  instance ``(\bar{G}, n - k)`` of VertexCover, where ``n`` is the number of
  vertices of G.

The function ``reduce`` validates the input using ``Clique.validate`` and then
produces a dictionary that conforms to the ``VertexCover`` format.  All edge
cases (k ≤ 0, k > n, etc.) are handled automatically by the arithmetic on ``k``
and by the definition of the target problem.
"""

from __future__ import annotations

from typing import Dict, List

from problems import Clique, VertexCover


def complement_edges(n: int, edges: List[List[int]]) -> List[List[int]]:
    """Return the edge list of the complement graph.

    The complement contains exactly those unordered pairs ``{u, v}`` with
    ``0 <= u < v < n`` that are *not* present in ``edges``.
    """
    # Build a set of frozensets for O(1) lookup.
    existing = {frozenset(e) for e in edges}
    comp: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in existing:
                comp.append([u, v])
    return comp


def reduce(instance: Dict) -> Dict:
    """Reduce a Clique instance to an equivalent VertexCover instance.

    Parameters
    ----------
    instance:
        A dictionary representing a Clique instance as described in
        ``problems.Clique``.

    Returns
    -------
    dict
        A dictionary representing a VertexCover instance that is a *yes*
        instance exactly when the original Clique instance is a *yes*
        instance.
    """
    # Validate the source instance.
    Clique.validate(instance)

    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Complement graph edges.
    comp_edges = complement_edges(n, edges)

    # Target parameter: vertex cover size at most n - k.
    k_target = n - k

    reduced = {"n": n, "edges": comp_edges, "k": k_target}
    # Validate the produced target instance (helps catch programming errors).
    VertexCover.validate(reduced)
    return reduced

