"""Reduction from Vertex Cover to Clique.

The source problem (Vertex Cover) and the target problem (Clique) are
 described in ``problems.py``.  An instance of each problem is a dictionary
 with the following keys:

* ``n`` – number of vertices, labelled ``0 .. n-1``.
* ``edges`` – list of undirected edges, each edge is a two‑element list
  ``[u, v]`` with ``u != v``.  The pair ``[u, v]`` and ``[v, u]`` represent the
  same edge and will not both appear.
* ``k`` – the parameter of the decision problem.

The reduction is the classic complement‑graph construction:

* A set ``C`` is a vertex cover of size ``k`` in ``G`` iff the complement
  ``V \ C`` is an independent set of size ``n - k``.
* An independent set in ``G`` corresponds to a clique of the same size in the
  complement graph ``G̅``.

Therefore we build the complement of the input graph and ask whether it
contains a clique of size ``n - k``.  This transformation runs in polynomial
time (quadratic in ``n``) and preserves the answer for all edge cases (e.g.
negative ``k`` or ``k`` larger than ``n``) because the definitions of the two
problems treat those situations consistently.
"""

from __future__ import annotations

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Vertex Cover instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary representing a Vertex Cover instance with keys ``n``,
        ``edges`` and ``k`` as described above.

    Returns
    -------
    dict
        A Clique instance.  The vertex set is unchanged, the edge set is the
        complement of the original edge set, and the new ``k`` value is
        ``n - k_original``.
    """

    n: int = instance["n"]
    original_edges: List[List[int]] = instance.get("edges", [])
    k_original: int = instance["k"]

    # Store original edges in a set of ordered tuples for O(1) look‑ups.
    edge_set = set()
    for u, v in original_edges:
        if u < v:
            edge_set.add((u, v))
        else:
            edge_set.add((v, u))

    # Build the complement graph.
    complement_edges: List[List[int]] = []
    for i in range(n):
        for j in range(i + 1, n):
            if (i, j) not in edge_set:
                complement_edges.append([i, j])

    # The new parameter for Clique.
    k_new = n - k_original

    return {"n": n, "edges": complement_edges, "k": k_new}
