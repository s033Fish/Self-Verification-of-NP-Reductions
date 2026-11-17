"""Reduction from Clique to Independent Set.

The reduction is the classic complement‑graph reduction:
    A set of vertices forms a clique in a graph G iff it forms an
    independent set in the complement of G.

The source problem (Clique) and the target problem (IndependentSet) share
the same instance format defined in ``problems.py``:

    {"n": int, "edges": [[u, v], ...], "k": int}

The ``reduce`` function takes a Clique instance and returns an IndependentSet
instance with the same number of vertices, the same ``k`` value, and the
edge list of the complement graph.

The implementation runs in O(n^2) time, which is polynomial in the size of
the input.
"""

from typing import List, Dict, Any


def _edge_key(u: int, v: int) -> tuple:
    """Return a canonical ordering for an undirected edge.

    Edges are stored as unordered pairs, so we always store the smaller
    vertex first to make set membership checks straightforward.
    """
    return (u, v) if u < v else (v, u)


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Clique instance to an Independent Set instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys ``n``, ``edges`` and ``k`` representing a
        Clique instance as described in ``problems.py``.

    Returns
    -------
    dict
        An Independent Set instance that is a yes‑instance exactly when the
        input Clique instance is a yes‑instance.
    """
    n = instance["n"]
    k = instance["k"]
    # Build a set of existing edges for O(1) look‑ups.
    original_edges = { _edge_key(u, v) for u, v in instance.get("edges", []) }

    # Complement edges: all unordered pairs of distinct vertices not in
    # original_edges.
    complement_edges: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if _edge_key(u, v) not in original_edges:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": k}
