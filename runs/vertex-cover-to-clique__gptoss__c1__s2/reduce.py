"""Reduction from Vertex Cover to Clique.

The source problem is **Vertex Cover** with instance format::

    {"n": n, "edges": [[u, v], ...], "k": k}

The target problem is **Clique** with the same structural format.  The
reduction is the classic complement‑graph construction:

* A set C of vertices is a vertex cover of size *k* in *G* iff the
  complement set I = V \ C is an independent set of size *n - k*.
* An independent set in *G* corresponds to a clique of the same size in
  the complement graph \bar G.

Therefore we output the complement graph and set the new parameter
``k' = n - k``.  This transformation preserves the answer for all edge
cases (negative *k*, *k* ≥ *n*, empty edge list, etc.) and runs in
polynomial time (O(n²)).
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Vertex Cover instance to a Clique instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` as
        described in the problem statement.

    Returns
    -------
    dict
        An instance of the Clique problem that is a yes‑instance exactly
        when the input instance is a yes‑instance.
    """

    n: int = instance["n"]
    k: int = instance["k"]
    original_edges: List[List[int]] = instance.get("edges", [])

    # Build a set for O(1) edge existence checks.  Edges are undirected,
    # so store each as a frozenset of its two endpoints.
    edge_set = {frozenset(e) for e in original_edges}

    # Complement edges: all unordered pairs (i, j) with i < j that are
    # not present in the original graph.
    complement_edges: List[List[int]] = []
    for i in range(n):
        for j in range(i + 1, n):
            if frozenset((i, j)) not in edge_set:
                complement_edges.append([i, j])

    # The target clique size is n - k (size of the independent set).
    target_k = n - k

    return {"n": n, "edges": complement_edges, "k": target_k}
