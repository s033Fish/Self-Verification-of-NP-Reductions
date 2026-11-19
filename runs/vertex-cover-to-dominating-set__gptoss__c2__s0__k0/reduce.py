"""Reduction from Vertex Cover to Dominating Set.

The source problem (VertexCover) instance format is:
    {"n": int, "edges": [[u, v], ...], "k": int}
where vertices are 0..n-1.

The target problem (DominatingSet) uses the same format.

We construct a graph G' from the input graph G as follows.

* For every edge (u, v) of G we add a new vertex e_uv that is adjacent
  only to u and v.  This forces any dominating set of size at most the
  budget to dominate e_uv via one of its endpoints, which exactly
  corresponds to covering the edge in a vertex cover.

* Vertices that are isolated in G (i.e., have no incident edge) would be
  problematic because a dominating set must contain them (or a neighbor),
  while a vertex cover does not need them.  For each isolated vertex v we
  attach a private leaf ℓ_v.  To dominate ℓ_v we must pick either v or ℓ_v.
  We give the reduction an extra budget of one for each isolated vertex,
  allowing the leaf to be chosen instead of the isolated vertex.

Formally, let I be the number of isolated vertices in G.  The constructed
instance has:
    n' = n + |E| + I
    k' = k + I
and the edge set described above.

Correctness sketch:
  * If G has a vertex cover C of size ≤ k, then D = C ∪ {leaf(v) | v isolated}
    is a dominating set of G' of size ≤ k + I = k'.  All edge‑gadgets are
    dominated because one of their endpoints lies in C, and isolated
    vertices are dominated by their private leaf.
  * Conversely, let D be a dominating set of G' with |D| ≤ k + I.
    For each isolated vertex v, at least one of {v, leaf(v)} belongs to D.
    Hence at most I vertices of D are used for isolated parts, leaving at
    most k vertices from the original vertex set.  Let C = D ∩ V(G).
    For any edge (u, v) the corresponding gadget vertex e_uv must be
    dominated, and its only neighbors are u and v, so at least one of them
    lies in C.  Thus C is a vertex cover of size ≤ k.

The reduction runs in polynomial time.
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a VertexCover instance to a DominatingSet instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys "n", "edges" and "k" describing a
        Vertex Cover instance.

    Returns
    -------
    dict
        A Dominating Set instance equivalent to the input.
    """

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge case: k < 0 → always a NO instance for Vertex Cover.
    # Return a trivially false Dominating Set instance (k' < 0).
    if k < 0:
        return {"n": 0, "edges": [], "k": -1}

    # Build adjacency information to find isolated vertices.
    adjacency: List[set[int]] = [set() for _ in range(n)]
    for u, v in edges:
        adjacency[u].add(v)
        adjacency[v].add(u)

    isolated_vertices: List[int] = [v for v in range(n) if not adjacency[v]]
    I: int = len(isolated_vertices)

    new_edges: List[List[int]] = []
    cur_vertex: int = n  # next fresh vertex index

    # Edge gadgets: for each original edge add a new vertex adjacent to its endpoints.
    for u, v in edges:
        e_idx = cur_vertex
        new_edges.append([u, e_idx])
        new_edges.append([v, e_idx])
        cur_vertex += 1

    # Leaves for isolated vertices.
    for v in isolated_vertices:
        leaf = cur_vertex
        new_edges.append([v, leaf])
        cur_vertex += 1

    new_n = cur_vertex
    new_k = k + I

    return {"n": new_n, "edges": new_edges, "k": new_k}

