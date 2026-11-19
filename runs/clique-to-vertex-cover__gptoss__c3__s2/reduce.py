"""Reduction from Clique to Vertex Cover.

The source problem is :class:`problems.Clique` and the target problem is
``VertexCover``.  For a graph ``G`` with ``n`` vertices we construct the
complement graph ``\overline{G}``.  It is well‑known that ``G`` contains a
clique of size ``k`` iff ``\overline{G}`` has a vertex cover of size
``n - k``.  This yields a polynomial‑time many‑one reduction.

The ``reduce`` function receives a Clique instance (a dict with keys
``"n"``, ``"edges"`` and ``"k"``) and returns a VertexCover instance in the
exact same format.
"""

from __future__ import annotations

from typing import List, Dict, Any

# Import the problem classes only for their validation helpers; the actual
# reduction does not depend on any heavy computation.
from problems import Clique, VertexCover


def _complement_edges(n: int, edges: List[List[int]]) -> List[List[int]]:
    """Return the edge list of the complement of the given undirected graph.

    ``edges`` is a list of ``[u, v]`` where ``0 <= u < v < n`` (the validation
    in :func:`problems.validate_graph` guarantees this).  The complement
    contains exactly those unordered pairs that are *not* present in the
    original edge set.
    """
    # Build a set for O(1) membership tests.
    existing = {frozenset((u, v)) for u, v in edges}
    comp: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in existing:
                comp.append([u, v])
    return comp


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Clique instance to a VertexCover instance.

    The transformation is:

    * ``n' = n`` (same number of vertices)
    * ``edges' = complement of edges``
    * ``k' = n - k``

    This runs in ``O(n^2)`` time, polynomial in the input size.
    """
    # Validate the source instance to catch malformed inputs early.
    Clique.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Compute complement edges and the new k.
    complement = _complement_edges(n, edges)
    new_k = n - k

    reduced = {"n": n, "edges": complement, "k": new_k}
    # Validate the target instance as a sanity check (optional but cheap).
    VertexCover.validate(reduced)
    return reduced

