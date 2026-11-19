"""Reduction from Vertex Cover to Dominating Set.

The source problem (``VertexCover``) expects instances of the form::

    {"n": int, "edges": [[u, v], ...], "k": int}

where ``n`` is the number of vertices (0‑based) and ``edges`` is a list of
undirected edges.  ``k`` is the size bound for the vertex cover.

The target problem (``DominatingSet``) uses the identical format – the same
dictionary keys – but the answer predicate is different (dominating set
instead of vertex cover).

We implement the classic polynomial‑time reduction that preserves the bound
``k`` exactly:

* Start with the original graph ``G = (V, E)`` where ``|V| = n``.
* Create a new graph ``G' = (V', E')`` where ``V' = V ∪ X``.
  ``X`` contains one fresh vertex ``x_e`` for every edge ``e = (u, v) ∈ E``.
* Add **all** possible edges among the original vertices – i.e. make ``V`` a
  clique.  These edges dominate the original part of the graph.
* For each original edge ``e = (u, v)`` connect its corresponding new vertex
  ``x_e`` to the two endpoints ``u`` and ``v`` (and to nothing else).

Why does this work?
-------------------
* Because ``V`` is a clique, any dominating set can be assumed to contain only
  original vertices – if a new vertex ``x_e`` were chosen, swapping it for one
  of its neighbours (either ``u`` or ``v``) does not increase the set size and
  still dominates everything.
* An original vertex dominates all of ``V``; the only vertices that still need
  domination are the ``x_e`` vertices.  Each ``x_e`` is adjacent precisely to
  the two endpoints of its edge, so to dominate ``x_e`` we must pick at least
  one of those endpoints.  Hence a dominating set restricted to ``V`` is
  exactly a vertex cover of the original graph.
* Conversely, any vertex cover of ``G`` dominates all ``x_e`` vertices and, by
  virtue of the clique, also dominates every original vertex.  Thus it is a
  dominating set of the same size.

Therefore ``G`` has a vertex cover of size ≤ ``k`` iff ``G'`` has a dominating
set of size ≤ ``k``.  The construction runs in polynomial time (quadratic in
``n`` because of the clique edges) and respects the required instance format.

The ``reduce`` function below performs this transformation.  It does **not**
invoke any solvers; it merely builds the new instance dictionary.
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Vertex Cover instance to a Dominating Set instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` describing a
        vertex‑cover problem as documented in ``problems.py``.

    Returns
    -------
    dict
        An instance of the Dominating Set problem with the same ``k`` value.
    """

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # New vertices: one for each original edge.
    m = len(edges)
    total_vertices = n + m

    new_edges: List[List[int]] = []

    # 1. Make the original vertices a clique.
    for u in range(n):
        for v in range(u + 1, n):
            new_edges.append([u, v])

    # 2. For each original edge, add connections to its dedicated new vertex.
    for idx, (u, v) in enumerate(edges):
        new_vertex = n + idx  # distinct id for this edge
        new_edges.append([u, new_vertex])
        new_edges.append([v, new_vertex])

    # Construct the target instance.
    return {"n": total_vertices, "edges": new_edges, "k": k}

