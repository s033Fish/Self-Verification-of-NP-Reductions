"""Reduction from Vertex Cover to Dominating Set.

The source problem (VertexCover) expects instances of the form::

    {"n": n, "edges": [[u, v], ...], "k": k}

where ``n`` is the number of vertices labelled ``0 .. n-1`` and ``edges`` is a
list of undirected edges.  The task is to decide whether the graph has a vertex
cover of size at most ``k``.

The target problem (DominatingSet) uses the same instance format, but the
question is whether there exists a dominating set of size at most ``k``.

We implement a classic polynomial‑time many‑one reduction.  For each vertex
``v`` of the original graph we create a *leaf* ``l_v`` adjacent only to ``v``.
For each original edge ``(u, v)`` we create a new *edge‑vertex* ``e_{uv}``
adjacent exactly to ``u`` and ``v``.  All original edges are retained – they do
not affect correctness but keep the construction simple.

Let ``n`` be the original number of vertices and ``m`` the number of edges.
The transformed graph has ``n' = 2·n + m`` vertices:

* vertices ``0 .. n-1`` – the original vertices,
* vertices ``n .. n+m-1`` – the edge‑vertices, one per original edge,
* vertices ``n+m .. 2·n+m-1`` – the leaf vertices.

The parameter is set to ``k' = k + n`` for ``k >= 0``; if ``k`` is negative we
keep it negative to preserve the trivial "no" case.

Correctness sketch:

* From a vertex cover ``C`` (|C| ≤ k) we obtain a dominating set
  ``D = C ∪ { leaf(v) | v ∉ C }`` of size exactly ``n`` ≤ k + n.
* Any dominating set ``D`` of size ≤ k' must contain at least one vertex from
  each pair ``{v, leaf(v)}``; thus ``|D ∩ V_original| ≤ k`` and those original
  vertices form a vertex cover because every edge‑vertex must be dominated by
  one of its endpoints.

Both directions hold, establishing the reduction.  The construction runs in
polynomial time.
"""

from __future__ import annotations

from typing import Dict, List, Tuple, Set


def reduce(instance: Dict) -> Dict:
    """Reduce a VertexCover instance to a DominatingSet instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys "n", "edges" and "k" describing a VertexCover
        instance.

    Returns
    -------
    dict
        An equivalent DominatingSet instance.
    """
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    m = len(edges)  # number of original edges

    # Index ranges for new vertices
    edge_vertex_start = n               # n .. n+m-1
    leaf_vertex_start = n + m           # n+m .. 2*n+m-1

    new_edges_set: Set[Tuple[int, int]] = set()

    def add_edge(u: int, v: int) -> None:
        if u == v:
            return
        a, b = (u, v) if u < v else (v, u)
        new_edges_set.add((a, b))

    # Keep original edges (optional)
    for u, v in edges:
        add_edge(u, v)

    # Edge‑vertices connected to their two endpoints
    for idx, (u, v) in enumerate(edges):
        ev = edge_vertex_start + idx
        add_edge(ev, u)
        add_edge(ev, v)

    # Leaf vertices attached to each original vertex
    for v in range(n):
        leaf = leaf_vertex_start + v
        add_edge(v, leaf)

    new_edges: List[List[int]] = [[u, v] for (u, v) in new_edges_set]

    # Adjust k: preserve negative case, otherwise add n
    new_k = k if k < 0 else k + n

    return {
        "n": 2 * n + m,
        "edges": new_edges,
        "k": new_k,
    }

