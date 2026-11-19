"""Reduction from Independent Set to Vertex Cover.

The source problem (Independent Set) asks whether a graph G = (V, E) has an
independent set of size at least k.  The target problem (Vertex Cover) asks
whether G has a vertex cover of size at most k'.  The classic complement
relationship yields a polynomial‑time many‑one reduction:

    S is an independent set  <=>  V \ S is a vertex cover.

Consequently, a YES instance of Independent Set with parameter k maps to a
YES instance of Vertex Cover with parameter k' = |V| - k, and vice‑versa.

The reduction simply copies the graph and replaces k with n - k.  This works
for all edge cases described in the problem statements:

* k <= 0  →  Independent Set is always YES; n - k >= n, and Vertex Cover is
  always YES because k' >= n.
* k > n  →  Independent Set is always NO; n - k < 0, and Vertex Cover is always
  NO because a negative k' cannot be satisfied.
* Empty edge set – the relationship still holds because any set of vertices
  (including the empty set) is both an independent set and a vertex cover.

The function runs in O(|V| + |E|) time, which is polynomial.
"""

from __future__ import annotations

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Independent Set instance to a Vertex Cover instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` following the
        format defined for :class:`IndependentSet` in ``problems.py``.

    Returns
    -------
    dict
        An instance of the Vertex Cover problem with the same vertex set and
        edge list, but with the parameter ``k' = n - k``.
    """
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # The reduction is simply the complement of the independent‑set size.
    new_k: int = n - k

    # Return a fresh dictionary; copying the edge list protects the caller
    # from accidental mutation.
    return {"n": n, "edges": [edge.copy() for edge in edges], "k": new_k}


__all__ = ["reduce"]
