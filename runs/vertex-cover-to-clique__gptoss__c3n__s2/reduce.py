"""Reduction from Vertex Cover to Clique.

The reduction uses the classic complement graph transformation:

    A graph G has a vertex cover of size ≤ k  ⇔  the complement of G has a
    clique of size ≥ n‑k.

Given an instance of ``VertexCover`` (a dict with keys ``n``, ``edges`` and
``k``) we construct the complement graph and set the new target ``k`` to
``n - k``.  The instance format of the target problem ``Clique`` is identical
to the source format, so the returned dictionary can be validated directly by
``Clique.validate``.

The implementation runs in O(n^2) time, which is polynomial in the size of
the input.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import VertexCover, Clique


def _complement_edges(n: int, edges: List[List[int]]) -> List[List[int]]:
    """Return the edge list of the complement of a simple undirected graph.

    ``edges`` is assumed to be a list of unordered pairs ``[u, v]`` with
    ``0 <= u, v < n`` and ``u != v``.  The complement contains exactly those
    unordered pairs that are *not* present in ``edges``.
    """
    # Store existing edges in a set of frozensets for O(1) look‑ups.
    seen = {frozenset(edge) for edge in edges}
    comp: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in seen:
                comp.append([u, v])
    return comp


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Vertex Cover instance to a Clique instance.

    The function validates the input using ``VertexCover.validate`` and then
    builds the complement graph.  The target ``k`` is ``n - k_src``.
    """
    # Validate the source instance – this will raise ``InvalidInstance`` if the
    # format is incorrect.
    VertexCover.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k_src: int = instance["k"]

    # Compute complement edges and the new k value.
    complement = _complement_edges(n, edges)
    k_target = n - k_src

    result: Dict[str, Any] = {"n": n, "edges": complement, "k": k_target}

    # Validate the produced target instance.
    Clique.validate(result)
    return result

