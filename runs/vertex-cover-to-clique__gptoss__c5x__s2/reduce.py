"""Reduction from Vertex Cover to Clique.

The reduction uses the classic complement graph transformation:

    G has a vertex cover of size ≤ k  ⇔  G's complement has an independent set
    of size ≥ n‑k  ⇔  G's complement has a clique of size ≥ n‑k.

Thus we construct the complement of the input graph and set the target ``k``
to ``n - k``.

Both the source (VertexCover) and target (Clique) problem classes are defined
in ``problems.py``. The ``reduce`` function validates the source instance, then
produces a target instance that satisfies the same answer condition.
"""

from __future__ import annotations

from typing import Dict, List

from problems import VertexCover, Clique, InvalidInstance


def complement_edges(n: int, edges: List[List[int]]) -> List[List[int]]:
    """Return the edge list of the complement graph on ``n`` vertices.

    ``edges`` is assumed to be a valid edge list for an undirected simple
    graph (no loops, no parallel edges). The complement contains exactly those
    unordered pairs ``{u, v}`` with ``u != v`` that are *not* present in the
    original edge set.
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
    """Reduce a VertexCover instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the VertexCover format.

    Returns
    -------
    dict
        A dictionary adhering to the Clique format such that the answer to
        the Clique instance is *yes* exactly when the answer to the original
        VertexCover instance is *yes*.
    """
    # Validate the source instance; this will raise InvalidInstance on malformed
    # input, matching the contract of the reduction framework.
    VertexCover.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Compute complement graph edges.
    comp_edges = complement_edges(n, edges)

    # The target parameter k' = n - k.
    target_k = n - k

    # Construct the target instance.
    target_instance: Dict = {"n": n, "edges": comp_edges, "k": target_k}

    # Validate the produced target instance to catch any programming errors.
    Clique.validate(target_instance)
    return target_instance

