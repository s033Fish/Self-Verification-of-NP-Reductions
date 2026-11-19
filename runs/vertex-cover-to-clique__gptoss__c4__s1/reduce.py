"""Reduction from Vertex Cover to Clique.

The classic polynomial‑time reduction uses the graph complement:

    G has a vertex cover of size at most k  <=>  the complement of G
    has a clique of size at least n - k.

Given an instance of :class:`VertexCover` (a dict with keys ``n``, ``edges``
and ``k``) this module constructs the corresponding Clique instance.

The implementation follows the specification in ``problems.py`` – the
returned instance must be a plain dictionary with the same fields as a
Clique instance.  No solvers are called; the transformation runs in
polynomial time (O(n^2) for the complement construction).
"""

from __future__ import annotations

from typing import List, Dict, Any, Set, Tuple

from problems import VertexCover, Clique


def _edge_key(u: int, v: int) -> Tuple[int, int]:
    """Return a canonical representation of an undirected edge.

    The input graph guarantees ``u != v`` and ``0 <= u, v < n``.  We store the
    edge as a sorted tuple so that ``(u, v)`` and ``(v, u)`` map to the same
    key.
    """

    return (u, v) if u < v else (v, u)


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Vertex Cover instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary representing a Vertex Cover problem as defined in
        ``problems.py``.

    Returns
    -------
    dict
        A Clique instance such that the original instance is a *yes*‑instance
        iff the returned instance is a *yes*‑instance.
    """

    # Validate the source instance – this raises InvalidInstance on malformed
    # input, matching the behaviour expected from other problem classes.
    VertexCover.validate(instance)

    n: int = instance["n"]
    original_edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Build a set of existing edges for O(1) membership tests.
    present: Set[Tuple[int, int]] = set()
    for u, v in original_edges:
        present.add(_edge_key(u, v))

    # Complement edges: all unordered pairs not present in the original graph.
    complement_edges: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in present:
                complement_edges.append([u, v])

    # The target k is n - original_k.
    target_k: int = n - k

    result: Dict[str, Any] = {
        "n": n,
        "edges": complement_edges,
        "k": target_k,
    }

    # Validate the constructed target instance before returning – this helps
    # catch programming errors early.
    Clique.validate(result)
    return result

