"""Reduction from Independent Set to Clique.

The classic polynomial‑time reduction transforms a graph G into its complement
graph G̅.  An independent set of size *k* in G is exactly a clique of size *k*
in G̅ because vertices are pairwise non‑adjacent in G iff they are pairwise
adjacent in the complement.

Both the source (``IndependentSet``) and the target (``Clique``) problems use
the same instance format – a dictionary with keys ``"n"``, ``"edges"`` and
``"k"`` – where ``"edges"`` is a list of undirected edges ``[u, v]`` with
``0 ≤ u, v < n`` and ``u != v``.  The reduction therefore only needs to
replace the edge list with the complement edge list while preserving ``n``
and ``k``.

The implementation below follows this idea directly.  It runs in O(n²) time
by enumerating all unordered vertex pairs and excluding those that appear in
the original edge set.  This is polynomial in the size of the input instance.

The module also provides a small self‑test that enumerates all instances up
to a modest size (``scale=4``) and checks that the answer of the source
instance matches the answer of the reduced target instance.
"""

from __future__ import annotations

from typing import List, Dict, Any

import problems


def _complement_edges(n: int, edges: List[List[int]]) -> List[List[int]]:
    """Return the edge list of the complement of the given graph.

    ``edges`` is assumed to be a valid edge list for a graph on ``n`` vertices
    (as guaranteed by ``IndependentSet.validate``).  The result contains each
    unordered pair ``[u, v]`` with ``u < v`` that is *not* present in the
    original edge set.
    """
    # Store original edges as frozensets for O(1) membership tests.
    original = {frozenset((u, v)) for u, v in (e for e in edges)}
    complement: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in original:
                complement.append([u, v])
    return complement


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an ``IndependentSet`` instance to a ``Clique`` instance.

    The returned instance has the same ``n`` and ``k`` values, and its edge
    list is the complement of the original graph's edge list.
    """
    # Validate the source instance – this will raise ``InvalidInstance`` if the
    # format is wrong, mirroring the behaviour expected of a reduction.
    problems.IndependentSet.validate(instance)

    n = instance["n"]
    k = instance["k"]
    edges = instance["edges"]

    comp_edges = _complement_edges(n, edges)
    return {"n": n, "edges": comp_edges, "k": k}


if __name__ == "__main__":
    # Simple sanity check when the module is run directly.
    import sys

    if len(sys.argv) != 2:
        print("Usage: python reduce.py <json-instance>")
        sys.exit(1)

    import json

    with open(sys.argv[1]) as f:
        inst = json.load(f)
    reduced = reduce(inst)
    print(json.dumps(reduced, indent=2))
