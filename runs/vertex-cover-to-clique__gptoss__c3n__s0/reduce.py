"""Reduction from Vertex Cover to Clique.

The classic reduction uses the complement graph.  Given a graph G = (V, E)
and an integer k, we construct the complement graph G' = (V, E') where
E' contains exactly those unordered pairs {u, v} that are *not* edges of G.
Then G has a vertex cover of size at most k iff G' has a clique of size at
least |V| - k.

Both the source (VertexCover) and target (Clique) problems are defined in
``problems.py``.  An instance is a plain ``dict`` with keys ``"n"``,
``"edges"`` and ``"k"``.  The reduction must return a new instance that
conforms to the target's format and preserves the answer.

The implementation runs in O(n^2) time, which is polynomial in the size of
the input instance.
"""

from __future__ import annotations

from typing import Dict, List

from problems import VertexCover, Clique


def _complement_edges(n: int, edges: List[List[int]]) -> List[List[int]]:
    """Return the edge list of the complement graph.

    ``edges`` is assumed to be a list of unordered pairs ``[u, v]`` with
    ``0 <= u, v < n`` and ``u != v``.  The complement contains every unordered
    pair that does *not* appear in ``edges``.
    """
    # Build a set for O(1) membership checks.
    existing = {frozenset((u, v)) for u, v in edges}
    comp: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in existing:
                comp.append([u, v])
    return comp


def reduce(instance: Dict) -> Dict:
    """Reduce a Vertex Cover instance to a Clique instance.

    The returned instance satisfies ``Clique.validate`` and the following
    equivalence holds:

    ``VertexCover.solve(instance)`` is ``True``  ⇔  ``Clique.solve`` on the
    returned instance is ``True``.
    """
    # Validate the source instance; this will raise ``InvalidInstance`` on bad
    # input, matching the behaviour expected by the testing harness.
    VertexCover.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Complement graph edges.
    comp_edges = _complement_edges(n, edges)

    # Target k' = n - k (size of independent set needed in G).
    target_k = n - k

    reduced = {"n": n, "edges": comp_edges, "k": target_k}
    # Ensure the produced instance is valid for Clique.
    Clique.validate(reduced)
    return reduced

