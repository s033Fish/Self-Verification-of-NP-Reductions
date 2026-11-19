"""Reduction from Clique to Vertex Cover.

The classic polynomial‑time many‑one reduction transforms an instance
``(G, k)`` of **Clique** into an instance ``(G̅, n - k)`` of **VertexCover**,
where ``G̅`` is the complement graph of ``G`` (the graph containing exactly
the non‑edges of ``G``) and ``n`` is the number of vertices.

Correctness sketch:
* ``G`` has a clique of size at least ``k`` ⇔ the complement ``G̅`` has a
  vertex cover of size at most ``n - k``.
* Edge‑cases line up because:
    - If ``k <= 0`` then ``n - k >= n`` and VertexCover is trivially yes.
    - If ``k > n`` then ``n - k < 0`` and VertexCover is trivially no.

The function ``reduce(instance)`` validates the input using the ``Clique``
class from ``problems.py`` and returns a dictionary that conforms to the
``VertexCover`` instance format.
"""

from __future__ import annotations

from typing import List, Dict, Set

from problems import Clique, VertexCover


def _complement_edges(n: int, edges: List[List[int]]) -> List[List[int]]:
    """Return the edge list of the complement graph.

    ``edges`` is assumed to be a valid list of undirected edges (no self‑loops
    and no duplicates). The complement contains exactly the unordered pairs
    ``{u, v}`` with ``0 <= u < v < n`` that are not present in ``edges``.
    """
    existing: Set[frozenset[int]] = {frozenset(e) for e in edges}
    comp: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in existing:
                comp.append([u, v])
    return comp


def reduce(instance: Dict) -> Dict:
    """Reduce a Clique instance to a VertexCover instance.

    Parameters
    ----------
    instance:
        A dictionary representing a Clique instance as described in
        ``problems.py``.

    Returns
    -------
    dict
        A VertexCover instance ``{"n": n, "edges": complement, "k": n - k}``.
    """
    # Validate the input according to the Clique specification.
    Clique.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Compute complement edges.
    comp_edges = _complement_edges(n, edges)

    # New parameter for VertexCover.
    new_k = n - k

    reduced_instance = {"n": n, "edges": comp_edges, "k": new_k}
    # Validate the produced instance as a proper VertexCover instance.
    VertexCover.validate(reduced_instance)
    return reduced_instance

