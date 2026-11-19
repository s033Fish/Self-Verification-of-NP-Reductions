"""Reduction from Clique to Independent Set.

The source problem is **Clique**:
    - Input: {"n": n, "edges": [[u, v], ...], "k": k}
    - Question: does the graph contain a clique of size **at least** ``k``?

The target problem is **IndependentSet** with the same instance format.

Standard polynomial‑time reduction:
    * Given a graph G construct its complement ``\overline{G}``.
    * A set of vertices is a clique in G iff it is an independent set
      in ``\overline{G}``.

Therefore we keep the vertex count ``n`` and the parameter ``k`` unchanged
and replace the edge list by the complement edge list.

The function ``reduce`` below implements exactly this transformation.
It runs in ``O(n^2)`` time, which is polynomial in the size of the input.
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Clique instance to an Independent Set instance.

    Parameters
    ----------
    instance:
        A dictionary with keys "n", "edges" and "k" following the
        format described in ``problems.py`` for the Clique problem.

    Returns
    -------
    dict
        An instance of the Independent Set problem that is a *yes*-instance
        exactly when the original Clique instance is a *yes*-instance.
    """

    n: int = instance["n"]
    k: int = instance["k"]
    # Original edges – store as a set of frozensets for O(1) lookup.
    original_edges = {frozenset(edge) for edge in instance.get("edges", [])}

    # Build complement edges: all unordered pairs {u, v} with u < v that are
    # *not* present in the original edge set.
    complement_edges: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if frozenset((u, v)) not in original_edges:
                complement_edges.append([u, v])

    return {"n": n, "edges": complement_edges, "k": k}
