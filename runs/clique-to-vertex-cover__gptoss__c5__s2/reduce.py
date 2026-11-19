"""Reduction from Clique to Vertex Cover.

The reduction is the classic complement‑graph transformation:

    G has a clique of size ≥ k  ⇔  the complement of G has a vertex cover
    of size ≤ n‑k.

Given an instance of :class:`Clique` (a graph ``G`` with ``n`` vertices and
edge list ``edges`` and integer ``k``) we construct an instance of
``VertexCover`` with the same number of vertices, edge list equal to the
complement of ``edges`` (i.e., all unordered pairs of distinct vertices that
are *not* edges in ``G``) and parameter ``k' = n - k``.

The transformation runs in O(n²) time, which is polynomial in the size of the
input.  Edge‑case handling follows directly from the properties of the
reduction and the definitions of the two problems (see the docstrings in
``problems.py``).
"""

from __future__ import annotations

from typing import Dict, List

from problems import Clique, VertexCover


def _complement_edges(n: int, edges: List[List[int]]) -> List[List[int]]:
    """Return the list of edges of the complement graph.

    ``edges`` is assumed to be a valid edge list for a simple undirected graph
    on vertices ``0..n-1`` (no duplicates, no self‑loops). The complement graph
    contains exactly those unordered pairs ``{u, v}`` with ``u != v`` that are
    *not* present in ``edges``.
    """
    # Build a set of frozensets for O(1) membership tests.
    existing = {frozenset(edge) for edge in edges}
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
    instance: dict
        A valid instance of :class:`Clique` as defined in ``problems.py``.

    Returns
    -------
    dict
        A valid instance of :class:`VertexCover` such that the answer to the
        returned instance is *yes* exactly when the answer to ``instance`` is
        *yes*.
    """
    # Validate the source instance. This will raise InvalidInstance if the
    # format is wrong, which mirrors the behaviour expected from a reduction.
    Clique.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Complement graph edges.
    comp_edges = _complement_edges(n, edges)

    # Target parameter.
    k_target = n - k

    target_instance: Dict = {"n": n, "edges": comp_edges, "k": k_target}
    # Validate the produced instance to catch programming errors early.
    VertexCover.validate(target_instance)
    return target_instance

