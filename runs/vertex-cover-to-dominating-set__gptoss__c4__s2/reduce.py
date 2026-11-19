"""Reduction from Vertex Cover to Dominating Set.

The source problem is VertexCover defined in ``problems.py``.
The target problem is DominatingSet defined in the same file.

Given a graph G = (V, E) and integer k, we construct a graph G' = (V', E') and
use the same k.  The construction is the classic reduction:

* Keep all original vertices that are incident to at least one edge (isolated
  vertices are irrelevant for vertex cover and would force a dominating set to
  contain them, breaking the equivalence).
* For each edge e = {u, v} create a new vertex w_e.
* Add edges (u, v) for every original edge (so original vertices can dominate
  each other) and also edges (u, w_e) and (v, w_e).

In G' every edge‑vertex w_e is adjacent only to its two original endpoints.
A dominating set of size ≤ k exists iff a vertex cover of size ≤ k exists in G.
The reduction runs in linear time.
"""

from __future__ import annotations

from typing import Dict, List

from problems import VertexCover, DominatingSet


def reduce(instance: Dict) -> Dict:
    """Reduce a VertexCover instance to a DominatingSet instance.

    Parameters
    ----------
    instance: dict with keys ``"n"``, ``"edges"`` and ``"k"``.

    Returns
    -------
    dict representing a DominatingSet instance.
    """
    # Validate source instance.
    VertexCover.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Determine vertices that actually appear in an edge.
    used_vertices = {u for u, v in edges} | {v for u, v in edges}
    # Map old vertex ids to a contiguous range for the new graph.
    old_to_new: Dict[int, int] = {old: new for new, old in enumerate(sorted(used_vertices))}
    v_cnt = len(old_to_new)

    # Build edge list for target graph.
    new_edges: List[List[int]] = []
    # Preserve original edges between used vertices.
    for u, v in edges:
        new_edges.append([old_to_new[u], old_to_new[v]])
    # Add a new vertex for each original edge and connect it to its endpoints.
    edge_vertices_start = v_cnt
    for i, (u, v) in enumerate(edges):
        w = edge_vertices_start + i
        new_edges.append([old_to_new[u], w])
        new_edges.append([old_to_new[v], w])

    new_instance: Dict = {
        "n": v_cnt + len(edges),
        "edges": new_edges,
        "k": k,
    }

    # Validate target instance.
    DominatingSet.validate(new_instance)
    return new_instance

