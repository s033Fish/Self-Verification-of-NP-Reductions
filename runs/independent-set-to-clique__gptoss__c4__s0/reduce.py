"""Reduction from Independent Set to Clique.

The classic reduction constructs the complement graph: a set of vertices is
independent in the original graph iff it is a clique in the complement.

Both the source (IndependentSet) and target (Clique) problems share the same
instance format – a dict with keys "n", "edges" and "k".  The reduction must
return a new instance that satisfies the validation rules of ``Clique`` and
preserves the answer.

The implementation is straightforward and runs in O(n^2) time, which is
polynomial in the size of the input.
"""

from __future__ import annotations

from typing import Dict, List

from problems import IndependentSet, Clique


def _complement_edges(n: int, edges: List[List[int]]) -> List[List[int]]:
    """Return the edge list of the complement graph.

    ``edges`` is assumed to be a list of undirected edges where each edge is a
    two‑element list ``[u, v]`` with ``u != v`` and ``0 <= u, v < n``.  The
    complement contains exactly those unordered pairs that are *not* present in
    ``edges``.
    """
    # Record existing edges in a set of frozensets for O(1) lookup.
    present = {frozenset((u, v)) for u, v in edges}
    comp: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in present:
                comp.append([u, v])
    return comp


def reduce(instance: Dict) -> Dict:
    """Reduce an Independent Set instance to a Clique instance.

    The returned instance has the same number of vertices ``n`` and the same
    target size ``k``.  Its edge list is the complement of the original graph.
    """
    # Validate the source instance – this will raise InvalidInstance if the
    # input is malformed.
    IndependentSet.validate(instance)

    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    complement = _complement_edges(n, edges)

    # Build the target instance.  Validation of the target will be performed by
    # the caller (or the oracle) when the reduction is used.
    target_instance: Dict = {"n": n, "edges": complement, "k": k}
    # Ensure the produced instance is valid for Clique.
    Clique.validate(target_instance)
    return target_instance

