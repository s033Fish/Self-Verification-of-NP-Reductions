"""Reduction from Vertex Cover to Dominating Set.

Given a graph G = (V, E) and integer k, we construct a graph G' as follows:
* Keep all vertices of V.
* For each edge {u, v} in E, add a new vertex w_{uv} and edges (u, w_{uv}) and (v, w_{uv}).
* Also keep the original edge (u, v) itself in the edge list.
The parameter k stays the same.

Claim: G has a vertex cover of size ≤ k iff G' has a dominating set of size ≤ k.
Proof sketch:
* If C is a vertex cover of G, then every edge‑vertex w_{uv} is adjacent to at least one endpoint in C,
  and because we also keep the original edge (u, v), any vertex in C dominates its neighbours in V as well.
  Hence C dominates all vertices of G', so C is a dominating set of size ≤ k.
* Conversely, let D be a dominating set of G' of size ≤ k. For each edge‑vertex w_{uv}, some neighbour (u or v) must be in D,
  otherwise w_{uv} would be undominated. Replacing any edge‑vertex present in D by one of its neighbours does not increase the size.
  The resulting set consists only of original vertices and hits at least one endpoint of every original edge, i.e., it is a vertex cover of G.

Isolated vertices are irrelevant for vertex cover, so they are removed before the construction.
If the original graph has no edges we output an empty graph, which is a trivial yes instance for both problems.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import VertexCover, DominatingSet


def _remove_isolated(n: int, edges: List[List[int]]) -> tuple[int, List[List[int]], Dict[int, int]]:
    """Return a subgraph containing only vertices that appear in at least one edge.
    Also returns a mapping from old vertex indices to new contiguous indices.
    """
    used = set()
    for u, v in edges:
        used.add(u)
        used.add(v)
    old_to_new: Dict[int, int] = {}
    new_idx = 0
    for i in range(n):
        if i in used:
            old_to_new[i] = new_idx
            new_idx += 1
    new_edges = [[old_to_new[u], old_to_new[v]] for u, v in edges]
    return new_idx, new_edges, old_to_new


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a VertexCover instance to a DominatingSet instance.
    The returned instance has the same k.
    """
    VertexCover.validate(instance)
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Remove isolated vertices – they do not affect vertex cover.
    n_active, edges_active, _ = _remove_isolated(n, edges)

    # No edges ⇒ empty graph works for both problems.
    if not edges_active:
        reduced = {"n": 0, "edges": [], "k": k}
        DominatingSet.validate(reduced)
        return reduced

    m = n_active                     # number of original vertices after removal
    e_cnt = len(edges_active)        # one new vertex per original edge
    total_vertices = m + e_cnt       # original vertices + edge‑vertices

    new_edges: List[List[int]] = []
    # Keep original edges to allow domination between original vertices.
    for u, v in edges_active:
        new_edges.append([u, v])
    # For each original edge add a new edge‑vertex adjacent to its endpoints.
    for i, (u, v) in enumerate(edges_active):
        ev = m + i
        new_edges.append([u, ev])
        new_edges.append([v, ev])

    reduced_instance = {"n": total_vertices, "edges": new_edges, "k": k}
    DominatingSet.validate(reduced_instance)
    return reduced_instance

