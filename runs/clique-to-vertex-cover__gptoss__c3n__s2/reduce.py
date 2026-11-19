"""Reduction from Clique to Vertex Cover.

Given an instance of the Clique problem (graph G with n vertices and a target
size k), we construct an instance of VertexCover on the complement graph G'.
The construction is classic:

* The complement graph has the same vertex set {0, ..., n-1}.
* For every unordered pair {u, v} with u < v that is **not** an edge of G we
  add the edge (u, v) to G'.
* The new parameter k' is set to n - k.

Correctness follows from the fact that a set of vertices forms a clique in G
iff it forms an independent set in the complement G'.  The complement of an
independent set is a vertex cover, and the sizes satisfy |VC| = n - |IS|.

The reduction runs in O(n^2) time, which is polynomial.
"""

from __future__ import annotations

from typing import Dict, List

from problems import Clique, VertexCover

def reduce(instance: Dict) -> Dict:
    """Reduce a Clique instance to a VertexCover instance.

    Parameters
    ----------
    instance: dict
        A valid Clique instance as defined in ``problems.py``.

    Returns
    -------
    dict
        A VertexCover instance that is a yes‑instance iff the input is a
        yes‑instance.
    """
    # Validate the source instance (will raise InvalidInstance on bad input).
    Clique.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Build a set of existing edges for O(1) look‑up.
    existing = {frozenset(edge) for edge in edges}

    # Complement edges: all unordered pairs not present in the original graph.
    complement_edges: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in existing:
                complement_edges.append([u, v])

    # New k value for vertex cover.
    k_target = n - k

    target_instance = {"n": n, "edges": complement_edges, "k": k_target}

    # Validate the target instance to ensure we produced a well‑formed one.
    VertexCover.validate(target_instance)
    return target_instance
