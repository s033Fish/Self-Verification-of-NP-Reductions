"""Reduction from Vertex Cover to Clique.

The source problem (Vertex Cover) and the target problem (Clique) are
defined in ``problems.py``.  Both use the same instance format:

    {"n": int, "edges": [[u, v], ...], "k": int}

The reduction is the classic complement‑graph reduction:

* A set C of vertices is a vertex cover of size ≤ k in a graph G
  iff V\C is an independent set of size ≥ n‑k.
* An independent set in G corresponds to a clique of the same size in the
  complement graph \bar G.

Therefore, given an instance (G, k) of Vertex Cover we construct the
complement graph \bar G and ask for a clique of size n‑k.

The transformation runs in polynomial time (O(n²) to build the complement
edges) and preserves the answer for all edge cases, as explained in the

docstring of the source and target problems.
"""

from typing import List, Dict, Any


def _edge_set(edges: List[List[int]]) -> set:
    """Return a set of unordered edge tuples for fast membership tests.

    The input edges are guaranteed to have ``u != v`` and no duplicate
    undirected edges, but we normalise them to ``(min, max)`` tuples.
    """
    return { (u, v) if u < v else (v, u) for u, v in edges }


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Vertex Cover instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` representing
        a Vertex Cover instance.

    Returns
    -------
    dict
        A Clique instance ``{"n": n, "edges": comp_edges, "k": n - k}``.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Build a set for O(1) membership checks.
    original = _edge_set(edges)

    # Complement edges: all unordered pairs not present in the original graph.
    comp_edges: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in original:
                comp_edges.append([u, v])

    # Target parameter is n - k.
    target_k = n - k

    return {"n": n, "edges": comp_edges, "k": target_k}

