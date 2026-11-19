"""Reduction from Clique to Independent Set.

The source problem *Clique* asks whether a given undirected graph G = (V, E)
contains a clique of size at least k.  The target problem *IndependentSet*
asks whether a graph contains an independent set of size at least k.

The classic polynomial‑time reduction uses the complement graph:
    G' = (V, \overline{E})
where \overline{E} contains exactly those unordered vertex pairs that are **not**
edges of G.  A set of vertices forms a clique in G iff it forms an independent
set in G'.  Therefore, the same integer k can be used for the target instance.

This file defines a single function ``reduce`` that takes an instance of the
source problem (as defined in ``problems.py``) and returns a correctly formatted
instance of the target problem.  The transformation runs in O(n^2) time, which
is polynomial in the size of the input.
"""

from typing import List, Dict, Any


def _edge_key(u: int, v: int) -> tuple:
    """Return a canonical representation for an undirected edge.

    The input edges may be given in any order, but we store them as sorted
    tuples so that look‑ups are O(1).
    """
    return (u, v) if u < v else (v, u)


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Clique instance to an Independent Set instance.

    Parameters
    ----------
    instance: dict
        ``{"n": n, "edges": [[u, v], ...], "k": k}`` describing the source
        Clique problem.

    Returns
    -------
    dict
        An instance of the Independent Set problem with the same ``n`` and
        ``k`` and with edges equal to the complement of the original edge set.
    """
    n: int = instance["n"]
    k: int = instance["k"]
    original_edges: List[List[int]] = instance.get("edges", [])

    # Build a set for O(1) membership tests.
    edge_set = set(_edge_key(u, v) for u, v in original_edges)

    # Compute complement edges.
    complement_edges: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if _edge_key(u, v) not in edge_set:
                complement_edges.append([u, v])

    # The target instance uses the same fields.
    return {"n": n, "edges": complement_edges, "k": k}
