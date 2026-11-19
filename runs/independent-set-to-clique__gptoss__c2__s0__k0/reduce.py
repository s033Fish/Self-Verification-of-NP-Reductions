"""Reduction from Independent Set to Clique.

The source problem is **Independent Set** with instance format::

    {"n": n, "edges": [[u, v], ...], "k": k}

The target problem is **Clique** with the same instance format.  The classic
polynomial‑time reduction uses the *complement graph*: a set of vertices is
independent in the original graph iff it is a clique in the complement.

The function ``reduce`` takes an Independent‑Set instance and returns a Clique
instance that is *yes* exactly when the input instance is *yes*.

Implementation details
----------------------
* ``n`` and ``k`` are copied unchanged.
* The edge list of the complement graph is constructed by enumerating all
  unordered vertex pairs ``(u, v)`` with ``0 <= u < v < n`` and keeping those
  pairs that are **not** present in the original edge set.
* The original edge list may contain each edge only once and never a self‑
  loop, as guaranteed by the problem specification.  We store the original
  edges in a ``set`` of ``(u, v)`` tuples with ``u < v`` for O(1) look‑ups.
* The resulting edge list follows the same convention – each edge appears
  exactly once with ``u < v``.

The algorithm runs in ``O(n^2)`` time, which is polynomial in the size of the
input instance.
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Independent‑Set instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` describing an
        Independent‑Set problem as documented in ``problems.py``.

    Returns
    -------
    dict
        A Clique instance (same keys) whose answer is *yes* exactly when the
        input instance's answer is *yes*.
    """

    n: int = int(instance["n"])  # number of vertices
    k: int = int(instance["k"])  # size parameter (copied unchanged)
    original_edges: List[List[int]] = instance.get("edges", [])

    # Store edges of G in a set for O(1) membership tests.  Ensure each edge
    # is represented with the smaller vertex first.
    edge_set = set()
    for u, v in original_edges:
        if u == v:
            # According to the specification this should never happen, but we
            # guard against it to keep the reduction well‑defined.
            continue
        a, b = (u, v) if u < v else (v, u)
        edge_set.add((a, b))

    # Build complement edges: all pairs not in edge_set.
    complement_edges: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in edge_set:
                complement_edges.append([u, v])

    # Return the Clique instance.
    return {"n": n, "edges": complement_edges, "k": k}

