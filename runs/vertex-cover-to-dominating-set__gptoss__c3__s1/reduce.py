"""Reduction from Vertex Cover to Dominating Set.

The source problem is :class:`VertexCover` (defined in ``problems.py``) and the
target problem is :class:`DominatingSet`.  Both problems use the same instance
format – a dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` – where ``n`` is
the number of vertices, ``edges`` is a list of undirected edges ``[u, v]`` and
``k`` is the size bound.

We implement the classic polynomial‑time many‑one reduction that preserves the
parameter ``k``:

* For every edge ``(u, v)`` of the original graph we introduce a fresh vertex
  ``w`` that is adjacent to **both** ``u`` and ``v``.
* The original edges are kept (they are irrelevant for the correctness of the
  reduction but do not hurt).
* Isolated vertices (vertices with degree 0) are removed before the construction.
  They do not affect the vertex‑cover answer, and keeping them would break the
  reduction because a dominating set would be forced to contain each isolated
  vertex.

Correctness sketch
-------------------
Let ``G`` be the input graph after removing isolated vertices, ``m`` its number
of edges and ``k`` the bound.

*If* ``G`` has a vertex cover ``C`` with ``|C| ≤ k`` then ``C`` dominates all
original vertices (any vertex not in ``C`` is adjacent to a vertex of ``C`` because
each of its incident edges is covered).  Moreover each new vertex ``w`` is
adjacent to an endpoint of its defining edge, which lies in ``C``.  Hence ``C``
is a dominating set of size at most ``k`` in the constructed graph ``G'``.

*Conversely*, suppose ``G'`` has a dominating set ``D`` with ``|D| ≤ k``.  If ``D``
contains a newly added vertex ``w`` we can replace ``w`` by one of its endpoints
without increasing the size of the set (the endpoint still dominates ``w`` and
all vertices that ``w`` dominated).  Repeating this yields a dominating set
``D'`` consisting only of original vertices and still of size ≤ k.  For each edge
``(u, v)`` the corresponding new vertex ``w`` must be dominated, therefore at
least one of ``u, v`` belongs to ``D'``.  Consequently ``D'`` is a vertex cover
of size ≤ k in the original graph.

The transformation runs in time linear in the size of the input graph, i.e.
polynomial time.
"""

from __future__ import annotations

from typing import Dict, List

def reduce(instance: Dict) -> Dict:
    """Reduce a Vertex Cover instance to a Dominating Set instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` describing a
        Vertex‑Cover instance.

    Returns
    -------
    dict
        An instance of the Dominating‑Set problem that is a *yes* instance iff the
        input instance is a *yes* instance.
    """
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Compute degree of each vertex to identify isolated vertices.
    degree = [0] * n
    for u, v in edges:
        degree[u] += 1
        degree[v] += 1

    # Mapping from old vertex index to new compact index (skip isolated).
    old_to_new = {}
    new_vertices = []
    for v in range(n):
        if degree[v] > 0:
            old_to_new[v] = len(new_vertices)
            new_vertices.append(v)
    n_compact = len(new_vertices)

    # Remap the original edges, discarding any that involve an isolated vertex
    # (there cannot be any because isolated vertices have degree 0).
    compact_edges: List[List[int]] = []
    for u, v in edges:
        nu = old_to_new[u]
        nv = old_to_new[v]
        compact_edges.append([nu, nv])

    m = len(compact_edges)
    # New vertices for each edge start after the compact original vertices.
    new_vertex_start = n_compact
    # Build the final edge list for the Dominating Set instance.
    ds_edges: List[List[int]] = []
    # Keep the original (compact) edges – they do not affect correctness.
    ds_edges.extend(compact_edges)
    # For each original edge add a new vertex adjacent to its two endpoints.
    for idx, (u, v) in enumerate(compact_edges):
        w = new_vertex_start + idx
        ds_edges.append([w, u])
        ds_edges.append([w, v])

    return {"n": n_compact + m, "edges": ds_edges, "k": k}

